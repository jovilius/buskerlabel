if [ "$1" == "vercel" ]; then
    # Run the web app on Vercel
    vercel link --yes
    vercel dev
else
    # Export secrets from .secrets
    while read -r line || [[ -n $line ]]; do    
        [[ "$line" =~ ^#.*$ || -z "$line" ]] && continue
        export $line
    done < .secrets
    # Run the web app locally
    uvicorn web:app
fi

