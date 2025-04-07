/**
 * Logs the current model selection and ensures it matches the format expected by the backend
 */
export const logModelSelection = (modelName: string): void => {
  console.log('Current model selection:', {
    selectedModel: modelName,
    expectedBackendFormat: modelName.toLowerCase(),
    isCorrectFormat: ['mobilenet_v2', 'inception_v3'].includes(modelName)
  });
};

/**
 * Ensures the model name is in the correct format for the backend
 */
export const getFormattedModelName = (modelName: string): string => {
  // Make sure model name is in correct format
  switch(modelName.toLowerCase()) {
    case 'mobilenet_v2':
    case 'mobilenetv2':
      return 'mobilenet_v2';
    case 'inception_v3':
    case 'inceptionv3':
      return 'inception_v3';
    default:
      console.warn(`Unknown model name: ${modelName}, defaulting to mobilenet_v2`);
      return 'mobilenet_v2';
  }
};
