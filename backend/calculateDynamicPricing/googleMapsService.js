const axios = require('axios');

const apiKey = "AIzaSyB1cfjM0hDHbd0tP3aYDZOd6C9tlRfyu6s"; // Access API key from environment variables

async function getDistanceMatrix(origin, destination) {
  const apiUrl = `https://maps.googleapis.com/maps/api/distancematrix/json?origins=${origin}&destinations=${destination}&key=${apiKey}`;

  try {
    const response = await axios.get(apiUrl);
    const data = response.data;

    if (data.status === 'OK') {
      if (data.rows[0].elements[0].status === 'OK') {
        const distance = data.rows[0].elements[0].distance.text;
        const duration = data.rows[0].elements[0].duration.text;
        return { distance, duration };
      } else {
        throw new Error(`Distance Matrix API error: ${data.rows[0].elements[0].status} - ${data.error_message || 'No error message provided'}`);
      }
    } else {
      throw new Error(`Distance Matrix API error: ${data.status} - ${data.error_message || 'No error message provided'}`);
    }
  } catch (error) {
    console.error('Error fetching distance matrix:', error.message);
    throw error;
  }
}

module.exports = { getDistanceMatrix };
