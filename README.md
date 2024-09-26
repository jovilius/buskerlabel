# BuskerLabel

## Development and Running Locally

To develop and run the FastAPI + Tailwind web application locally, follow these steps:

### Build Tailwind CSS

To build Tailwind CSS:

1. Navigate to the `tailwindcss` folder:
   ```bash
   cd tailwindcss
   ```
2. Run the following command to build Tailwind CSS:
   ```bash
   npm run build
   ```

### Set Up Virtual Environment and Install Dependencies

- Activate the virtual environment:
  ```bash
  source venv/bin/activate
  ```
- Install the required libraries from `requirements.txt`:
  ```bash
  pip install -r requirements.txt
  ```

### Run Locally with Environment Variables from Your Machine

- Ensure the `.secret` file contains the following environment variables:

  - `POSTGRES_URL`
  - `OPENAI_API_KEY`

- Run the application locally:
  ```bash
  ./run_local.sh
  ```

### Run Locally with Vercel Environment Variables

- To run the application locally with Vercel's environment settings, use the following command:
  ```bash
  ./run_local.sh vercel
  ```

## Deployment on Vercel

To deploy the application to Vercel:

1. Commit your changes to the `main` branch.
2. Push the changes to the `main` branch:
   ```bash
   git push origin main
   ```

Vercel will automatically detect the changes and deploy the updated application.
