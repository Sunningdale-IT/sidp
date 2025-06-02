{{/*
Expand the name of the chart.
*/}}
{{- define "idp.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "idp.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "idp.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "idp.labels" -}}
helm.sh/chart: {{ include "idp.chart" . }}
{{ include "idp.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "idp.selectorLabels" -}}
app.kubernetes.io/name: {{ include "idp.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Web component labels
*/}}
{{- define "idp.web.labels" -}}
{{ include "idp.labels" . }}
app.kubernetes.io/component: web
{{- end }}

{{/*
Web selector labels
*/}}
{{- define "idp.web.selectorLabels" -}}
{{ include "idp.selectorLabels" . }}
app.kubernetes.io/component: web
{{- end }}

{{/*
Celery component labels
*/}}
{{- define "idp.celery.labels" -}}
{{ include "idp.labels" . }}
app.kubernetes.io/component: celery
{{- end }}

{{/*
Celery selector labels
*/}}
{{- define "idp.celery.selectorLabels" -}}
{{ include "idp.selectorLabels" . }}
app.kubernetes.io/component: celery
{{- end }}

{{/*
Celery Beat component labels
*/}}
{{- define "idp.celeryBeat.labels" -}}
{{ include "idp.labels" . }}
app.kubernetes.io/component: celery-beat
{{- end }}

{{/*
Celery Beat selector labels
*/}}
{{- define "idp.celeryBeat.selectorLabels" -}}
{{ include "idp.selectorLabels" . }}
app.kubernetes.io/component: celery-beat
{{- end }}

{{/*
Flower component labels
*/}}
{{- define "idp.flower.labels" -}}
{{ include "idp.labels" . }}
app.kubernetes.io/component: flower
{{- end }}

{{/*
Flower selector labels
*/}}
{{- define "idp.flower.selectorLabels" -}}
{{ include "idp.selectorLabels" . }}
app.kubernetes.io/component: flower
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "idp.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "idp.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the image name
*/}}
{{- define "idp.image" -}}
{{- $registry := .Values.global.imageRegistry | default .Values.image.registry -}}
{{- $repository := .Values.image.repository -}}
{{- $tag := .Values.image.tag | default .Chart.AppVersion -}}
{{- if $registry }}
{{- printf "%s/%s:%s" $registry $repository $tag }}
{{- else }}
{{- printf "%s:%s" $repository $tag }}
{{- end }}
{{- end }}

{{/*
PostgreSQL host
*/}}
{{- define "idp.postgresql.host" -}}
{{- if .Values.postgresql.enabled }}
{{- printf "%s-postgresql" (include "idp.fullname" .) }}
{{- else }}
{{- .Values.externalPostgresql.host }}
{{- end }}
{{- end }}

{{/*
PostgreSQL port
*/}}
{{- define "idp.postgresql.port" -}}
{{- if .Values.postgresql.enabled }}
{{- 5432 }}
{{- else }}
{{- .Values.externalPostgresql.port }}
{{- end }}
{{- end }}

{{/*
PostgreSQL database
*/}}
{{- define "idp.postgresql.database" -}}
{{- if .Values.postgresql.enabled }}
{{- .Values.postgresql.auth.database }}
{{- else }}
{{- .Values.externalPostgresql.database }}
{{- end }}
{{- end }}

{{/*
PostgreSQL username
*/}}
{{- define "idp.postgresql.username" -}}
{{- if .Values.postgresql.enabled }}
{{- .Values.postgresql.auth.username }}
{{- else }}
{{- .Values.externalPostgresql.username }}
{{- end }}
{{- end }}

{{/*
Redis host
*/}}
{{- define "idp.redis.host" -}}
{{- if .Values.redis.enabled }}
{{- printf "%s-redis-master" (include "idp.fullname" .) }}
{{- else }}
{{- .Values.externalRedis.host }}
{{- end }}
{{- end }}

{{/*
Redis port
*/}}
{{- define "idp.redis.port" -}}
{{- if .Values.redis.enabled }}
{{- 6379 }}
{{- else }}
{{- .Values.externalRedis.port }}
{{- end }}
{{- end }}

{{/*
Redis URL
*/}}
{{- define "idp.redis.url" -}}
{{- $host := include "idp.redis.host" . -}}
{{- $port := include "idp.redis.port" . -}}
{{- printf "redis://%s:%s/0" $host ($port | toString) }}
{{- end }} 
