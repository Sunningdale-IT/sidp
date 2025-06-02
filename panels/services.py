import requests
import docker
import json
from kubernetes import client, config
from django.core.cache import cache
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class DynamicDataService:
    """Service to fetch dynamic data from various sources."""
    
    def fetch_data(self, data_source):
        """Fetch data from a dynamic data source with caching."""
        cache_key = f"dynamic_data_{data_source.id}"
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            return cached_data
        
        try:
            if data_source.source_type == 'docker_registry':
                data = self._fetch_docker_images(data_source)
            elif data_source.source_type == 'kubernetes_api':
                data = self._fetch_kubernetes_resources(data_source)
            elif data_source.source_type == 'git_repository':
                data = self._fetch_git_branches(data_source)
            elif data_source.source_type == 'custom_api':
                data = self._fetch_custom_api(data_source)
            else:
                raise ValueError(f"Unsupported source type: {data_source.source_type}")
            
            # Cache the data
            cache.set(cache_key, data, data_source.cache_duration)
            return data
            
        except Exception as e:
            logger.error(f"Error fetching data from {data_source.name}: {str(e)}")
            raise
    
    def _fetch_docker_images(self, data_source):
        """Fetch Docker images from a registry."""
        try:
            # Parse registry URL and repository
            url_parts = data_source.endpoint_url.split('/')
            registry = url_parts[2] if len(url_parts) > 2 else 'docker.io'
            repository = '/'.join(url_parts[3:]) if len(url_parts) > 3 else ''
            
            # Use Docker SDK to list images
            client = docker.from_env()
            images = client.images.list()
            
            # Filter and format images
            image_list = []
            for image in images[:10]:  # Limit to latest 10 images
                if image.tags:
                    for tag in image.tags:
                        if repository in tag:
                            image_list.append({
                                'value': tag,
                                'label': tag,
                                'created': image.attrs.get('Created', '')
                            })
            
            return sorted(image_list, key=lambda x: x.get('created', ''), reverse=True)
            
        except Exception as e:
            logger.error(f"Error fetching Docker images: {str(e)}")
            return []
    
    def _fetch_kubernetes_resources(self, data_source):
        """Fetch Kubernetes resources."""
        try:
            # Load Kubernetes config
            try:
                config.load_incluster_config()  # For in-cluster usage
            except:
                config.load_kube_config()  # For local development
            
            v1 = client.CoreV1Api()
            
            # Determine resource type from endpoint
            if 'namespaces' in data_source.endpoint_url:
                namespaces = v1.list_namespace()
                return [
                    {'value': ns.metadata.name, 'label': ns.metadata.name}
                    for ns in namespaces.items
                ]
            elif 'pods' in data_source.endpoint_url:
                pods = v1.list_pod_for_all_namespaces()
                return [
                    {
                        'value': pod.metadata.name,
                        'label': f"{pod.metadata.name} ({pod.metadata.namespace})"
                    }
                    for pod in pods.items[:20]  # Limit results
                ]
            
            return []
            
        except Exception as e:
            logger.error(f"Error fetching Kubernetes resources: {str(e)}")
            return []
    
    def _fetch_git_branches(self, data_source):
        """Fetch Git repository branches."""
        try:
            import git
            
            # Clone or open repository
            repo_url = data_source.endpoint_url
            # This is a simplified implementation
            # In production, you'd want to handle authentication and caching properly
            
            return [
                {'value': 'main', 'label': 'main'},
                {'value': 'develop', 'label': 'develop'},
                {'value': 'feature/new-feature', 'label': 'feature/new-feature'},
            ]
            
        except Exception as e:
            logger.error(f"Error fetching Git branches: {str(e)}")
            return []
    
    def _fetch_custom_api(self, data_source):
        """Fetch data from a custom API endpoint."""
        try:
            headers = {}
            
            # Handle authentication
            if data_source.authentication_method == 'bearer_token':
                token = data_source.auth_config.get('token', '')
                headers['Authorization'] = f'Bearer {token}'
            elif data_source.authentication_method == 'api_key':
                key = data_source.auth_config.get('key', '')
                headers['X-API-Key'] = key
            
            response = requests.get(
                data_source.endpoint_url,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Transform data to expected format
            if isinstance(data, list):
                return [
                    {'value': item, 'label': str(item)}
                    for item in data
                ]
            elif isinstance(data, dict) and 'items' in data:
                return [
                    {'value': item.get('id', item), 'label': item.get('name', str(item))}
                    for item in data['items']
                ]
            
            return []
            
        except Exception as e:
            logger.error(f"Error fetching custom API data: {str(e)}")
            return []

