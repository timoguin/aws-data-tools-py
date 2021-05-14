nohup $MAVEN_CONFIG/.venv/bin/moto_server --host 0.0.0.0 --port 4615 &
echo "Pausing for moto to warm up ..." >&2
sleep 2

# Create the org
AWS_ACCESS_KEY_ID=dummy AWS_SECRET_ACCESS_KEY=dummy \
  aws --region=us-east-1 --endpoint=http://localhost:4566 organizations create-organization --feature-set ALL
