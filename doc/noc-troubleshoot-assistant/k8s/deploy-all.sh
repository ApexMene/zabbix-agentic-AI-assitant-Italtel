#!/bin/bash
# Complete deployment of NOC Troubleshooting Assistant to EKS
# Includes Zabbix instances and all components

set -e

CLUSTER_NAME="noc-troubleshoot-cluster"
NAMESPACE="noc-app"
REGION="us-west-2"

echo "=========================================="
echo "NOC Troubleshooting Assistant"
echo "Complete EKS Deployment"
echo "=========================================="
echo ""

# Configure kubectl
echo "Configuring kubectl for cluster $CLUSTER_NAME..."
aws eks update-kubeconfig --name $CLUSTER_NAME --region $REGION

# 1. Base resources
echo ""
echo "1. Creating base resources..."
kubectl apply -f k8s/base/namespace.yaml
kubectl apply -f k8s/base/service-account.yaml
kubectl apply -f k8s/base/configmap-app.yaml
kubectl apply -f k8s/base/configmap-instances.yaml
kubectl apply -f k8s/base/configmap-postgres-init.yaml
kubectl apply -f k8s/base/configmap-runbooks.yaml

# 2. External Secrets Operator
echo ""
echo "2. Installing External Secrets Operator..."
helm repo add external-secrets https://charts.external-secrets.io 2>/dev/null || true
helm repo update
helm upgrade --install external-secrets external-secrets/external-secrets \
  -n external-secrets-system \
  --create-namespace \
  --wait

# 3. External Secrets
echo ""
echo "3. Setting up External Secrets..."
kubectl apply -f k8s/secrets/external-secrets.yaml
echo "   Waiting for secrets to sync..."
sleep 15

# 4. Storage
echo ""
echo "4. Creating Persistent Volume Claims..."
kubectl apply -f k8s/storage/persistent-volumes.yaml

# 5. Databases
echo ""
echo "5. Deploying databases..."
kubectl apply -f k8s/deployments/postgres.yaml
kubectl apply -f k8s/deployments/zabbix-backbone.yaml
kubectl apply -f k8s/deployments/zabbix-5gcore.yaml

echo "   Waiting for databases to be ready..."
kubectl wait --for=condition=ready pod -l app=postgres -n $NAMESPACE --timeout=180s
kubectl wait --for=condition=ready pod -l app=zabbix-backbone-postgres -n $NAMESPACE --timeout=180s
kubectl wait --for=condition=ready pod -l app=zabbix-5gcore-postgres -n $NAMESPACE --timeout=180s

# 6. Zabbix Servers
echo ""
echo "6. Waiting for Zabbix servers..."
kubectl wait --for=condition=ready pod -l app=zabbix-backbone-server -n $NAMESPACE --timeout=180s
kubectl wait --for=condition=ready pod -l app=zabbix-5gcore-server -n $NAMESPACE --timeout=180s

# 7. Zabbix Web
echo ""
echo "7. Waiting for Zabbix web interfaces..."
kubectl wait --for=condition=ready pod -l app=zabbix-backbone-web -n $NAMESPACE --timeout=120s
kubectl wait --for=condition=ready pod -l app=zabbix-5gcore-web -n $NAMESPACE --timeout=120s

# 8. MCP Server
echo ""
echo "8. Deploying MCP Server..."
kubectl apply -f k8s/deployments/mcp-server.yaml
kubectl wait --for=condition=ready pod -l app=mcp-server -n $NAMESPACE --timeout=120s

# 9. Backend
echo ""
echo "9. Deploying Backend..."
kubectl apply -f k8s/deployments/backend.yaml
kubectl wait --for=condition=ready pod -l app=backend -n $NAMESPACE --timeout=120s

# 10. Frontend
echo ""
echo "10. Deploying Frontend..."
kubectl apply -f k8s/deployments/frontend.yaml
kubectl wait --for=condition=ready pod -l app=frontend -n $NAMESPACE --timeout=120s

# Summary
echo ""
echo "=========================================="
echo "✅ Deployment Complete!"
echo "=========================================="
echo ""
echo "Services deployed:"
kubectl get pods -n $NAMESPACE
echo ""
echo "Getting LoadBalancer URL..."
kubectl get svc frontend-service -n $NAMESPACE
echo ""
echo "Access the application at the EXTERNAL-IP:80"
echo ""
echo "Zabbix Web Interfaces (internal):"
echo "  Backbone: http://zabbix-backbone-web:8080"
echo "  5G Core:  http://zabbix-5gcore-web:8080"
