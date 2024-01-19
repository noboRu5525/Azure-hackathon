# **Manual**

Application Name: Taskman
Release Date: January 15, 2024

### **Purpose of the Manual**

The purpose of this manual is to ensure that users can successfully launch and verify the operation of the application.

### **Overview of the Application**

Taskman is an application where AI automatically generates and manages tasks.

### **Technologies Used**

- Docker
- Flask
- Azure OpenAI
- MySQL
- Nginx
- JavaScript
- CSS

### **Preparations Before Starting**

Installation of Docker

### **Required Tools**

Docker

### **Initial Setup and Installation Procedure**

In any desired directory, execute the following command to download:

```bash
git clone https://github.com/noboRu5525/Azure-hackathon.git

```

### **Basic Operation (Launching)**

Navigate to the cloned directory:

```jsx
cd Azure-hackathon

```

Insert your Azure OpenAI **API key** and **endpoint** information into the .env file, and place it in the same directory as the docker-compose.yml file:

```markdown
AZURE_OPENAI_KEY=******************
AZURE_OPENAI_ENDPOINT=**************

```

Launch the application with:

```jsx
docker-compose up --build

```

After launching, connect to **[http://localhost](http://localhost/)** in your browser.

### **Extension**

When extending the functionality and using external libraries, add them to **requirements.txt**. Afterwards, rebuild the application with:

```css
docker-compose up --build

```

This manual is designed to guide users through the setup and basic use of the Taskman application, ensuring a smooth and successful experience.
docker-compose up --build
This manual is designed to guide users through the setup and basic use of the Taskman application, ensuring a smooth and successful experience.
