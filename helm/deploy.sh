#!/bin/bash

# IDP Helm Chart Deployment Script
# This script helps deploy the Internal Developer Platform to Kubernetes

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
NAMESPACE="idp"
RELEASE_NAME="idp"
VALUES_FILE=""
DRY_RUN=false
UPGRADE=false

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Deploy the Internal Developer Platform (IDP) to Kubernetes using Helm.

OPTIONS:
    -n, --namespace NAMESPACE    Kubernetes namespace (default: idp)
    -r, --release RELEASE        Helm release name (default: idp)
    -f, --values VALUES_FILE     Values file to use (optional)
    -u, --upgrade               Upgrade existing release
    -d, --dry-run               Perform a dry run
    -h, --help                  Show this help message

EXAMPLES:
    # Install with default values
    $0

    # Install with custom values file
    $0 -f values-production.yaml

    # Install in custom namespace
    $0 -n my-idp-namespace

    # Upgrade existing installation
    $0 -u -f values-production.yaml

    # Dry run to see what would be deployed
    $0 -d -f values-production.yaml

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--namespace)
            NAMESPACE="$2"
            shift 2
            ;;
        -r|--release)
            RELEASE_NAME="$2"
            shift 2
            ;;
        -f|--values)
            VALUES_FILE="$2"
            shift 2
            ;;
        -u|--upgrade)
            UPGRADE=true
            shift
            ;;
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Check if we're in the right directory
if [[ ! -f "idp-chart/Chart.yaml" ]]; then
    print_error "Chart.yaml not found. Please run this script from the helm/ directory."
    exit 1
fi

print_status "Starting IDP deployment..."
print_status "Namespace: $NAMESPACE"
print_status "Release: $RELEASE_NAME"
if [[ -n "$VALUES_FILE" ]]; then
    print_status "Values file: $VALUES_FILE"
fi

# Check prerequisites
print_status "Checking prerequisites..."

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed or not in PATH"
    exit 1
fi

# Check if helm is available
if ! command -v helm &> /dev/null; then
    print_error "helm is not installed or not in PATH"
    exit 1
fi

# Check if we can connect to Kubernetes cluster
if ! kubectl cluster-info &> /dev/null; then
    print_error "Cannot connect to Kubernetes cluster. Please check your kubeconfig."
    exit 1
fi

print_success "Prerequisites check passed"

# Add required Helm repositories
print_status "Adding required Helm repositories..."
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Update chart dependencies
print_status "Updating chart dependencies..."
cd idp-chart
helm dependency update
cd ..

# Create namespace if it doesn't exist
if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
    print_status "Creating namespace: $NAMESPACE"
    kubectl create namespace "$NAMESPACE"
else
    print_status "Namespace $NAMESPACE already exists"
fi

# Prepare Helm command
HELM_CMD="helm"
if [[ "$UPGRADE" == "true" ]]; then
    HELM_CMD="$HELM_CMD upgrade"
else
    HELM_CMD="$HELM_CMD install"
fi

HELM_CMD="$HELM_CMD $RELEASE_NAME ./idp-chart"
HELM_CMD="$HELM_CMD --namespace $NAMESPACE"

if [[ "$UPGRADE" == "false" ]]; then
    HELM_CMD="$HELM_CMD --create-namespace"
fi

if [[ -n "$VALUES_FILE" ]]; then
    if [[ ! -f "$VALUES_FILE" ]]; then
        print_error "Values file not found: $VALUES_FILE"
        exit 1
    fi
    HELM_CMD="$HELM_CMD -f $VALUES_FILE"
fi

if [[ "$DRY_RUN" == "true" ]]; then
    HELM_CMD="$HELM_CMD --dry-run --debug"
fi

# Execute Helm command
print_status "Executing: $HELM_CMD"
if eval "$HELM_CMD"; then
    if [[ "$DRY_RUN" == "false" ]]; then
        print_success "IDP deployment completed successfully!"
        
        # Show deployment status
        print_status "Checking deployment status..."
        kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/name=idp
        
        # Show services
        print_status "Services:"
        kubectl get services -n "$NAMESPACE" -l app.kubernetes.io/name=idp
        
        # Show ingress if enabled
        if kubectl get ingress -n "$NAMESPACE" &> /dev/null; then
            print_status "Ingress:"
            kubectl get ingress -n "$NAMESPACE"
        fi
        
        # Show access information
        echo ""
        print_success "Deployment Information:"
        echo "  Namespace: $NAMESPACE"
        echo "  Release: $RELEASE_NAME"
        echo ""
        print_status "To check the status of your deployment:"
        echo "  kubectl get all -n $NAMESPACE"
        echo ""
        print_status "To view logs:"
        echo "  kubectl logs -f deployment/idp-web -n $NAMESPACE"
        echo "  kubectl logs -f deployment/idp-celery -n $NAMESPACE"
        echo ""
        print_status "To access the application:"
        echo "  kubectl port-forward service/idp-web 8000:8000 -n $NAMESPACE"
        echo "  Then visit: http://localhost:8000"
        echo ""
        print_status "To uninstall:"
        echo "  helm uninstall $RELEASE_NAME -n $NAMESPACE"
        
    else
        print_success "Dry run completed successfully!"
    fi
else
    print_error "Deployment failed!"
    exit 1
fi 
