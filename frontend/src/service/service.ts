// apiService.js

// Define the base URL of your FastAPI backend.
// This should be the address where your FastAPI server is running.
// You might want to move this to an environment variable for production.
const BASE_URL = process.env.BACKEND_BASE_URL || 'http://127.0.0.1:8000';

/**
 * Sends a question to the RAG pipeline.
 * @param {string} question - The question to be processed by the pipeline.
 * @returns {Promise<any>} The JSON response from the API.
 * @throws {Error} If the network request fails or the response is not ok.
 */
export const askQuestion = async (question: string, memory: string[]) => {
  // Construct the full URL for the /ask endpoint.
  const url = `${BASE_URL}/ask`;

  // Define the request body in a JSON format.
  const requestBody = { question: question, memory: memory };

  try {
    // Perform the POST request using the native fetch API.
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      // Convert the JavaScript object to a JSON string.
      body: JSON.stringify(requestBody),
    });

    // Check if the response was successful (status code 200-299).
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Network response was not ok');
    }

    // Parse and return the JSON response.
    const data = await response.json();
    console.log(data)
    console.log(JSON.parse(data['answer']))
    return JSON.parse(data['answer']);
  } catch (error) {
    // Log and re-throw the error for the calling component to handle.
    console.error('Error in askQuestion:', error);
    throw error;
  }
};

/**
 * Uploads a file for processing by the RAG pipeline.
 * @param {File} file - The file object to upload.
 * @returns {Promise<any>} The JSON response from the API.
 * @throws {Error} If the network request fails or the response is not ok.
 */
export const uploadAndProcessFile = async (file: any) => {
  // Construct the full URL for the /upload_and_process endpoint.
  const url = `${BASE_URL}/upload_and_process`;

  // Create a new FormData object to handle file uploads.
  const formData = new FormData();
  // Append the file to the form data.
  formData.append('file', file);

  try {
    // Perform the POST request. The 'Content-Type' header is automatically
    // set by the browser when using FormData, so we don't need to specify it.
    const response = await fetch(url, {
      method: 'POST',
      body: formData,
    });

    // Check for a successful response.
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Network response was not ok');
    }

    // Parse and return the JSON response.
    const data = await response.json();
    return data;
  } catch (error) {
    // Log and re-throw the error for the calling component.
    console.error('Error in uploadAndProcessFile:', error);
    throw error;
  }
};
