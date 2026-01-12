#!/bin/bash
# Deploy NOC Troubleshooting Assistant to EKS
# Run this after EKS cluster is ready

set -e

CLUSTER_NAME="noc-troubleshoot-cluster"
NAMESPACE="noc-app"

echo "=========================================="
echo "Deploying NOC App to EKS"
echo "=========================================="
echo ""

# 1. Create namespace
echo "1. Creating namespace..."
kubectl apply -f k8s/base/namespace.yaml

# 2. Create service account
echo "2. Creating service account (IRSA)..."
kubectl apply -f k8s/base/service-account.yaml

# 3. Install External Secrets Operator
echo "3. Installing External Secrets Operator..."
helm repo add external-secrets https://charts.external-secrets.io
helm repo update
helm install external-secrets external-secrets/external-secrets \
  -n external-secrets-system \
  --create-namespace \
  --wait

# 4. Create ConfigMaps
echo "4. Creating ConfigMaps..."
kubectl apply -f k8s/base/configmap-app.yaml
kubectl apply -f k8s/base/configmap-instances.yaml

# 5. Create External Secrets
echo "5. Setting up External Secrets..."
kubectl apply -f k8s/secrets/external-secrets.yaml

# Wait for secrets to sync
echo "   Waiting for secrets to sync from AWS..."
sleep 10

# 6. Create PVCs
echo "6. Creating Persistent Volume Claims..."
kubectl apply -f k8s/storage/persistent-volumes.yaml

# 7. Deploy PostgreSQL
echo "7. Deploying PostgreSQL..."
kubectl apply -f k8s/deployments/postgres.yaml
kubectl wait --for=condition=ready pod -l app=postgres -n $NAMESPACE --timeout=120s

# 8. Deploy MCP Server
echo "8. Deploying MCP Server..."
kubectl apply -f k8s/deployments/mcp-server.yaml
kubectl wait --for=condition=ready pod -l app=mcp-server -n $NAMESPACE --timeout=120s

# 9. Deploy Backend
echo "9. Deploying Backend..."
kubectl apply -f k8s/deployments/backend.yaml
kubectl wait --for=condition=ready pod -l app=backend -n $NAMESPACE --timeout=120s

# 10. Deploy Frontend
echo "10. Deploying Frontend..."
kubectl apply -f k8s/deployments/frontend.yaml
kubectl wait --for=condition=ready pod -l app=frontend -n $NAMESPACE --timeout=120s

# 11. Get LoadBalancer URL
echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "Getting LoadBalancer URL..."
kubectl get svc frontend-service -n $NAMESPACE

echo ""
echo "Access the application at the EXTERNAL-IP shown above"
echo "It may take a few minutes for the LoadBalancer to be provisioned"
