# Internal Developer Platform - Data Flow Diagram

## Overview
This diagram illustrates how data flows through the Internal Developer Platform (IDP), from user interactions to operation execution and monitoring.

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                USER INTERFACE LAYER                                │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐                │
│  │   Dashboard     │    │   Admin Panel   │    │   API Clients   │                │
│  │   (Templates)   │    │   (Django)      │    │   (External)    │                │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘                │
│           │                       │                       │                        │
└───────────┼───────────────────────┼───────────────────────┼────────────────────────┘
            │                       │                       │
            ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              APPLICATION LAYER                                     │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐                │
│  │   Core Views    │    │   Panel Views   │    │ Operation Views │                │
│  │   - Dashboard   │    │   - List/CRUD   │    │   - Execute     │                │
│  │   - Health      │    │   - Submit      │    │   - Monitor     │                │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘                │
│           │                       │                       │                        │
│           ▼                       ▼                       ▼                        │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐                │
│  │  Core Services  │    │ Panel Services  │    │Operation Services│                │
│  │   - Auth        │    │   - Dynamic     │    │   - Executor    │                │
│  │   - Logging     │    │   - Data        │    │   - Validator   │                │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘                │
│           │                       │                       │                        │
└───────────┼───────────────────────┼───────────────────────┼────────────────────────┘
            │                       │                       │
            ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                               DATA LAYER                                           │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐                │
│  │   PostgreSQL    │    │     Redis       │    │   File System   │                │
│  │   - Models      │    │   - Cache       │    │   - Logs        │                │
│  │   - Relations   │    │   - Sessions    │    │   - Static      │                │
│  │   - Migrations  │    │   - Tasks       │    │   - Media       │                │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘                │
│           │                       │                       │                        │
└───────────┼───────────────────────┼───────────────────────┼────────────────────────┘
            │                       │                       │
            ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                            BACKGROUND PROCESSING                                   │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐                │
│  │ Celery Workers  │    │  Celery Beat    │    │    Flower       │                │
│  │   - Execute     │    │   - Schedule    │    │   - Monitor     │                │
│  │   - Process     │    │   - Periodic    │    │   - Dashboard   │                │
│  │   - Log         │    │   - Tasks       │    │   - Stats       │                │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘                │
│           │                       │                       │                        │
└───────────┼───────────────────────┼───────────────────────┼────────────────────────┘
            │                       │                       │
            ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           EXTERNAL INTEGRATIONS                                    │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐                │
│  │   Kubernetes    │    │   Docker Hub    │    │   Git Repos     │                │
│  │   - API Calls   │    │   - Images      │    │   - Branches    │                │
│  │   - Resources   │    │   - Tags        │    │   - Commits     │                │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘                │
│                                                                                     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐                │
│  │   Cloud APIs    │    │   Custom APIs   │    │   Monitoring    │                │
│  │   - Azure       │    │   - Internal    │    │   - Prometheus  │                │
│  │   - AWS         │    │   - External    │    │   - Health      │                │
│  │   - GCP         │    │   - Services    │    │   - Metrics     │                │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘                │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

## Detailed Data Flow Scenarios

### 1. Panel Submission Flow

```
User Dashboard → Panel Form → Panel Submission → Operation Execution → Results
     │               │              │                    │              │
     ▼               ▼              ▼                    ▼              ▼
┌─────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────┐
│ Browse  │   │ Fill Form   │   │ Validate    │   │ Execute     │   │ Display │
│ Panels  │──▶│ Fields      │──▶│ Data        │──▶│ Commands    │──▶│ Status  │
└─────────┘   └─────────────┘   └─────────────┘   └─────────────┘   └─────────┘
                    │                    │                    │
                    ▼                    ▼                    ▼
              ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
              │ Dynamic     │   │ Store in    │   │ Log to      │
              │ Data Load   │   │ Database    │   │ Operations  │
              └─────────────┘   └─────────────┘   └─────────────┘
```

### 2. Operation Execution Flow

```
Operation Template → Parameter Substitution → Security Validation → Execution → Logging
        │                      │                       │              │         │
        ▼                      ▼                       ▼              ▼         ▼
┌─────────────┐      ┌─────────────────┐      ┌─────────────┐   ┌─────────┐  ┌─────────┐
│ Load        │      │ Replace         │      │ Check       │   │ Run     │  │ Store   │
│ Template    │─────▶│ {{variables}}   │─────▶│ Dangerous   │──▶│ Command │─▶│ Results │
└─────────────┘      └─────────────────┘      └─────────────┘   └─────────┘  └─────────┘
        │                      │                       │              │         │
        ▼                      ▼                       ▼              ▼         ▼
┌─────────────┐      ┌─────────────────┐      ┌─────────────┐   ┌─────────┐  ┌─────────┐
│ Get Panel   │      │ User Input      │      │ Command     │   │ Celery  │  │ Update  │
│ Submission  │      │ Data            │      │ Whitelist   │   │ Task    │  │ Status  │
└─────────────┘      └─────────────────┘      └─────────────┘   └─────────┘  └─────────┘
```

### 3. Dynamic Data Loading Flow

```
Panel Field → Data Source → External API → Cache → Response → UI Update
     │             │             │          │        │          │
     ▼             ▼             ▼          ▼        ▼          ▼
┌─────────┐  ┌─────────────┐  ┌─────────┐  ┌─────┐  ┌─────────┐  ┌─────────┐
│ Request │  │ Check       │  │ Call    │  │ Set │  │ Format  │  │ Populate│
│ Options │─▶│ Cache       │─▶│ API     │─▶│Cache│─▶│ Data    │─▶│ Dropdown│
└─────────┘  └─────────────┘  └─────────┘  └─────┘  └─────────┘  └─────────┘
                   │                                      │
                   ▼                                      ▼
             ┌─────────────┐                        ┌─────────────┐
             │ Return      │                        │ Transform   │
             │ Cached Data │                        │ to Options  │
             └─────────────┘                        └─────────────┘
```

## Database Schema Relationships

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│      User       │     │   BaseModel     │     │  SecretStore    │
│ ─────────────── │     │ ─────────────── │     │ ─────────────── │
│ + username      │     │ + created_at    │     │ + name          │
│ + email         │◄────┤ + updated_at    │     │ + key_vault     │
│ + password      │     │ + created_by    │     │ + secret_name   │
└─────────────────┘     │ + updated_by    │     │ + description   │
                        └─────────────────┘     └─────────────────┘
                                 ▲                        ▲
                                 │                        │
                                 │                        │
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│     Panel       │     │   PanelField    │     │ DynamicDataSrc  │
│ ─────────────── │     │ ─────────────── │     │ ─────────────── │
│ + title         │◄────┤ + name          │     │ + name          │
│ + description   │     │ + field_type    │     │ + source_type   │
│ + order         │     │ + is_required   │     │ + endpoint_url  │
│ + is_active     │     │ + options       │     │ + auth_config   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                        │
         ▼                        ▼
┌─────────────────┐     ┌─────────────────┐
│ PanelSubmission │     │ OperationTemplate│
│ ─────────────── │     │ ─────────────── │
│ + data (JSON)   │     │ + name          │
│ + status        │◄────┤ + operation_type│
│ + user          │     │ + command_template│
└─────────────────┘     │ + timeout       │
         │               └─────────────────┘
         ▼                        │
┌─────────────────┐              ▼
│OperationExecution│    ┌─────────────────┐
│ ─────────────── │     │ OperationLog    │
│ + status        │     │ ─────────────── │
│ + executed_cmd  │────▶│ + level         │
│ + output        │     │ + message       │
│ + error_output  │     │ + timestamp     │
└─────────────────┘     └─────────────────┘
```

## API Data Flow

```
┌─────────────────┐
│   API Request   │
│ ─────────────── │
│ GET /api/panels │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ Authentication  │
│ ─────────────── │
│ Session Check   │
│ Permissions     │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│   ViewSet       │
│ ─────────────── │
│ PanelViewSet    │
│ Serialization   │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│   Database      │
│ ─────────────── │
│ Query Panels    │
│ Apply Filters   │
└─────────────────┘
```

## Celery Task Processing

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Task Trigger   │     │   Redis Queue   │     │ Celery Worker   │
│ ─────────────── │     │ ─────────────── │     │ ─────────────── │
│ Panel Submit    │────▶│ Task Queue      │────▶│ Execute Task    │
│ Operation Run   │     │ Task Status     │     │ Update Status   │
│ Scheduled Job   │     │ Result Store    │     │ Log Progress    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                          │
                                                          ▼
                                                ┌─────────────────┐
                                                │   Task Result   │
                                                │ ─────────────── │
                                                │ Success/Failure │
                                                │ Output Data     │
                                                │ Error Messages  │
                                                └─────────────────┘
```

## Security Data Flow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  User Request   │     │  Authentication │     │   Authorization │
│ ─────────────── │     │ ─────────────── │     │ ─────────────── │
│ HTTP Request    │────▶│ Session Check   │────▶│ Permission Check│
│ Headers/Cookies │     │ User Validation │     │ Role Validation │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                          │
                                                          ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Command Exec   │     │  Validation     │     │   Audit Log     │
│ ─────────────── │     │ ─────────────── │     │ ─────────────── │
│ Template Load   │◄────┤ Security Check  │────▶│ Action Logging  │
│ Parameter Sub   │     │ Whitelist Check │     │ User Tracking   │
│ Safe Execution  │     │ Dangerous Block │     │ Result Storage  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Monitoring and Observability

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Application   │     │   Metrics       │     │   Monitoring    │
│ ─────────────── │     │ ─────────────── │     │ ─────────────── │
│ Django Views    │────▶│ Prometheus      │────▶│ Health Checks   │
│ Celery Tasks    │     │ Custom Metrics  │     │ Status Pages    │
│ Database Ops    │     │ Performance     │     │ Alerting        │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Logging      │     │   Flower        │     │   Dashboard     │
│ ─────────────── │     │ ─────────────── │     │ ─────────────── │
│ Structured Logs │     │ Task Monitor    │     │ Real-time Stats │
│ Error Tracking  │     │ Worker Status   │     │ Activity Feed   │
│ Audit Trail     │     │ Queue Stats     │     │ System Health   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Key Data Entities

### Core Models
- **User**: Authentication and authorization
- **BaseModel**: Common fields (timestamps, audit)
- **SecretStore**: Secure secret references

### Panel Models
- **Panel**: Configuration containers
- **PanelField**: Dynamic form fields
- **PanelSubmission**: User input data
- **DynamicDataSource**: External data integration

### Operation Models
- **OperationTemplate**: Command templates
- **OperationExecution**: Execution instances
- **OperationLog**: Detailed logging
- **SecretMapping**: Secret to operation mapping

## Data Flow Principles

1. **Separation of Concerns**: Clear boundaries between UI, business logic, and data
2. **Security First**: All operations validated and logged
3. **Async Processing**: Long-running tasks handled by Celery
4. **Caching Strategy**: Redis for performance optimization
5. **Audit Trail**: Complete logging of all user actions
6. **Scalability**: Stateless design for horizontal scaling
7. **Monitoring**: Comprehensive observability at all layers

This data flow architecture ensures secure, scalable, and maintainable operation of the Internal Developer Platform. 
