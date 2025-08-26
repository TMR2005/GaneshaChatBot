import { TranscribeResponse } from '../types';

const API_BASE_URL = 'http://localhost:5000';

export async function transcribeAudio(audioBlob: Blob): Promise<TranscribeResponse> {
  const formData = new FormData();
  formData.append('audio', audioBlob, 'audio.webm');

  const response = await fetch(`${API_BASE_URL}/transcribe`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error || 'Failed to transcribe audio');
  }

  return response.json();
}

export async function sendTextMessage(message: string): Promise<TranscribeResponse> {
  // Make a POST request to a new '/text-message' endpoint
  const response = await fetch(`${API_BASE_URL}/text-message`, {
    method: 'POST',
    headers: {
      // Set the content type to JSON
      'Content-Type': 'application/json',
    },
    // Send the message in the request body as a JSON object
    body: JSON.stringify({ message }),
  });

  // Handle errors, similar to the transcribeAudio function
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({})); // Graceful fallback
    throw new Error(errorData.error || 'Failed to send text message');
  }

  // Parse and return the successful JSON response
  return response.json();
}