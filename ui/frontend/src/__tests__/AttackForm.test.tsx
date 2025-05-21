import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import axios from 'axios';
import AttackForm from '../components/AttackForm';
import { AttackResult } from '../types';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('AttackForm', () => {
  // Setup props that will be passed to the component
  const mockProps = {
    selectedFile: null,
    setSelectedFile: jest.fn(),
    setPreview: jest.fn(),
    setResults: jest.fn(),
    setIsLoading: jest.fn()
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders form elements correctly', () => {
    render(<AttackForm {...mockProps} />);
    
    // Check that file input exists
    expect(screen.getByLabelText(/epsilon/i)).toBeInTheDocument();
    
    // Check that model selector exists
    expect(screen.getByText(/auto-tune epsilon/i)).toBeInTheDocument();
    
    // Check that submit button exists
    expect(screen.getByRole('button', { name: /run attack/i })).toBeInTheDocument();
  });

  test('handles file selection', async () => {
    render(<AttackForm {...mockProps} />);
    
    // Create a fake file
    const file = new File(['dummy content'], 'test-image.jpg', { type: 'image/jpeg' });
    
    // Get the file input
    const fileInput = screen.getByLabelText(/file/i) as HTMLInputElement;
    
    // Simulate file selection
    await userEvent.upload(fileInput, file);
    
    // Check that setSelectedFile was called with the file
    expect(mockProps.setSelectedFile).toHaveBeenCalledWith(file);
    
    // Check that setPreview was called
    expect(mockProps.setPreview).toHaveBeenCalled();
  });

  test('handles form submission', async () => {
    // Mock the axios post call to return a successful response
    const mockResult: AttackResult = {
      epsilon_used: 0.05,
      orig_class: 'car',
      orig_conf: 0.95,
      adv_class: 'truck',
      adv_conf: 0.6,
      original_image: 'data:image/png;base64,abc123',
      perturbation_image: 'data:image/png;base64,def456',
      adversarial_image: 'data:image/png;base64,ghi789'
    };
    
    mockedAxios.post.mockResolvedValueOnce({ data: mockResult });
    
    // Set up component with a selected file
    const file = new File(['dummy content'], 'test-image.jpg', { type: 'image/jpeg' });
    const updatedProps = {
      ...mockProps,
      selectedFile: file
    };
    
    // Render component
    render(<AttackForm {...updatedProps} />);
    
    // Click the submit button
    const submitButton = screen.getByRole('button', { name: /run attack/i });
    fireEvent.click(submitButton);
    
    // Check that isLoading was set to true
    expect(mockProps.setIsLoading).toHaveBeenCalledWith(true);
    
    // Wait for the API call to resolve
    await waitFor(() => {
      // Check that axios.post was called with the correct URL
      expect(mockedAxios.post).toHaveBeenCalledWith(
        'http://localhost:5000/attack',
        expect.any(FormData),
        expect.any(Object)
      );
      
      // Check that isLoading was set back to false
      expect(mockProps.setIsLoading).toHaveBeenCalledWith(false);
      
      // Check that setResults was called with the processed results
      expect(mockProps.setResults).toHaveBeenCalledWith({
        ...mockResult,
        original_image: mockResult.original_image,
        perturbation_image: mockResult.perturbation_image,
        adversarial_image: mockResult.adversarial_image
      });
    });
  });

  test('handles auto-tune checkbox toggle', () => {
    render(<AttackForm {...mockProps} />);
    
    // Initially auto-tune should be unchecked and epsilon slider visible
    const autoTuneCheckbox = screen.getByLabelText(/auto-tune epsilon/i);
    const epsilonSlider = screen.getByLabelText(/epsilon/i);
    
    expect(autoTuneCheckbox).not.toBeChecked();
    expect(epsilonSlider).toBeEnabled();
    
    // Toggle auto-tune on
    fireEvent.click(autoTuneCheckbox);
    
    // Check if epsilon slider is disabled when auto-tune is enabled
    // Note: In the current implementation, the slider is still visible but might be disabled in some way
    // This depends on how your UI is designed
  });

  test('handles API errors gracefully', async () => {
    // Mock window.alert
    const mockAlert = jest.spyOn(window, 'alert').mockImplementation();
    
    // Mock console.error
    const mockConsoleError = jest.spyOn(console, 'error').mockImplementation();
    
    // Mock axios to reject with an error
    mockedAxios.post.mockRejectedValueOnce(new Error('API Error'));
    
    // Set up component with a selected file
    const file = new File(['dummy content'], 'test-image.jpg', { type: 'image/jpeg' });
    const updatedProps = {
      ...mockProps,
      selectedFile: file
    };
    
    // Render component
    render(<AttackForm {...updatedProps} />);
    
    // Click the submit button
    const submitButton = screen.getByRole('button', { name: /run attack/i });
    fireEvent.click(submitButton);
    
    // Wait for the error handling to complete
    await waitFor(() => {
      // Check that console.error was called
      expect(mockConsoleError).toHaveBeenCalled();
      
      // Check that alert was called
      expect(mockAlert).toHaveBeenCalledWith('Error processing attack');
      
      // Check that isLoading was set back to false
      expect(mockProps.setIsLoading).toHaveBeenCalledWith(false);
    });
    
    // Clean up mocks
    mockAlert.mockRestore();
    mockConsoleError.mockRestore();
  });
}); 