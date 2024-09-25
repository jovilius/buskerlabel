# Export secrets from .secrets
while read -r line || [[ -n $line ]]; do    
    [[ "$line" =~ ^#.*$ || -z "$line" ]] && continue
    export $line
done < .secrets

# Run the web app on localhost
uvicorn web:app
