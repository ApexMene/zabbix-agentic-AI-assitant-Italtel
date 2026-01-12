# EKS Deployment Guide

## Prerequisites
- AWS CLI configured
- kubectl installed
- Helm installed
- EKS cluster created

## Architecture

All components deployed in single EKS cluster:
- **Namespace**: `noc-app`
- **Region**: `us-west-2`
- **Cluster**: `noc-troubleshoot-cluster`

### Components (11 total):
1. PostgreSQL (NOC database)
2. Zabbix Backbone PostgreSQL
3. Zabbix Backbone Server
4. Zabbix Backbone Web
5. Zabbix 5G Core PostgreSQL
6. Zabbix 5G Core Server
7. Zabbix 5G Core Web
8. MCP Server (2 replicas)
9. Backend (2 replicas)
10. Frontend (2 replicas)
11. External Secrets Operator

## Deployment

### Quick Deploy
```bash
cd k8s
./deploy-all.sh
```

### Manual Deploy
```bash
# 1. Configure kubectl
aws eks update-kubeconfig --name noc-troubleshoot-cluster --region us-west-2

# 2. Deploy base resources
kubectl apply -f base/

# 3. Install External Secrets Operator
helm repo add external-secrets https://charts.external-secrets.io
helm install external-secrets external-secrets/external-secrets \
  -n external-secrets-system --create-namespace

# 4. Deploy secrets
kubectl apply -f secrets/

# 5. Deploy storage
kubectl apply -f storage/

# 6. Deploy applications
kubectl apply -f deployments/
```

## Access

### Get LoadBalancer URL
```bash
kubectl get svc frontend-service -n noc-app
```

Access at: `http://<EXTERNAL-IP>`

### Internal Services
- Backend API: `http://backend-service:13001`
- MCP Server: `http://mcp-server-service:13002`
- Zabbix Backbone: `http://zabbix-backbone-web:8080`
- Zabbix 5G Core: `http://zabbix-5gcore-web:8080`

## Monitoring

```bash
# Check all pods
kubectl get pods -n noc-app

# Check logs
kubectl logs -f deployment/backend -n noc-app
kubectl logs -f deployment/mcp-server -n noc-app

# Check secrets sync
kubectl get externalsecrets -n noc-app
```

## Scaling

```bash
# Scale backend
kubectl scale deployment backend -n noc-app --replicas=3

# Scale MCP server
kubectl scale deployment mcp-server -n noc-app --replicas=4
```

## Troubleshooting

### Pods not starting
```bash
kubectl describe pod <pod-name> -n noc-app
kubectl logs <pod-name> -n noc-app
```

### Secrets not syncing
```bash
kubectl get externalsecrets -n noc-app
kubectl describe externalsecret <name> -n noc-app
```

### Database connection issues
```bash
kubectl exec -it postgres-0 -n noc-app -- psql -U noc_user -d noc_db
```

## Cleanup

```bash
# Delete all resources
kubectl delete namespace noc-app

# Delete EKS cluster
aws cloudformation delete-stack --stack-name eks-noc-troubleshoot-cluster-stack --region us-west-2
```
