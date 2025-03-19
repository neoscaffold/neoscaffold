# Utilize the Node.js 14 official image
FROM node:18

# Define the working directory
WORKDIR /usr/src/app

# Clone package.json and package-lock.json
COPY package*.json ./

# Copy .npmrc file
COPY .npmrc ./

# Set up all the dependencies
RUN npm config set registry https://registry.npmjs.org/ && npm ci --no-audit --no-fund

# Globally set up Ember CLI
RUN npm i -g ember-cli@5.8.1

# Clone all files
COPY . .

ARG NEOSCAFFOLD_URL
ARG GOOGLE_SIGN_IN_CLIENT_ID

# GET ENV SECRETS

ENV NEOSCAFFOLD_URL $NEOSCAFFOLD_URL
ENV GOOGLE_SIGN_IN_CLIENT_ID $GOOGLE_SIGN_IN_CLIENT_ID

# Make the application’s port accessible
ARG PORT=4200
EXPOSE ${PORT}

# Launch the application
CMD ["ember", "serve", "--environment", "production"]