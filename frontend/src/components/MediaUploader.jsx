import React, { useState, useRef } from 'react';

/**
 * Enterprise MediaUploader component for HomiQ.
 * Supports image & document preview, drag-and-drop, upload progress,
 * format validation, size limit checks, error alerts, and deletion.
 */
export default function MediaUploader({
  uploadFunction,
  onUploadSuccess,
  onDeleteSuccess,
  currentImageUrl = null,
  assetType = 'profile_avatar',
  accept = 'image/jpeg,image/png,image/webp',
  maxSizeMB = 5,
  label = 'Upload Media',
  disabled = false,
  allowDelete = true,
}) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(currentImageUrl);
  const [isUploading, setIsUploading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const validateFile = (file) => {
    setErrorMessage('');
    setSuccessMessage('');

    if (!file) return false;

    // Size check
    const maxSizeBytes = maxSizeMB * 1024 * 1024;
    if (file.size > maxSizeBytes) {
      setErrorMessage(`File size (${(file.size / (1024 * 1024)).toFixed(1)}MB) exceeds maximum ${maxSizeMB}MB.`);
      return false;
    }

    // Type check
    const acceptedTypes = accept.split(',').map((t) => t.trim().toLowerCase());
    const fileType = file.type.toLowerCase();
    const isAccepted = acceptedTypes.some((type) => {
      if (type.endsWith('/*')) {
        const base = type.replace('/*', '');
        return fileType.startsWith(base);
      }
      return fileType === type;
    });

    if (!isAccepted && acceptedTypes.length > 0) {
      setErrorMessage(`File type not allowed. Please upload ${accept}.`);
      return false;
    }

    return true;
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file && validateFile(file)) {
      setSelectedFile(file);
      if (file.type.startsWith('image/')) {
        setPreviewUrl(URL.createObjectURL(file));
      } else {
        setPreviewUrl(null);
      }
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    if (!disabled) setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (disabled) return;

    const file = e.dataTransfer.files?.[0];
    if (file && validateFile(file)) {
      setSelectedFile(file);
      if (file.type.startsWith('image/')) {
        setPreviewUrl(URL.createObjectURL(file));
      } else {
        setPreviewUrl(null);
      }
    }
  };

  const handleUpload = async () => {
    if (!selectedFile || !uploadFunction) return;

    setIsUploading(true);
    setErrorMessage('');
    setSuccessMessage('');

    try {
      const response = await uploadFunction(selectedFile);
      setSuccessMessage(response?.message || 'File uploaded successfully!');
      setSelectedFile(null);
      if (onUploadSuccess) {
        onUploadSuccess(response);
      }
    } catch (err) {
      setErrorMessage(err.message || 'Upload failed. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleDelete = async () => {
    if (!onDeleteSuccess) return;

    setIsUploading(true);
    setErrorMessage('');
    setSuccessMessage('');

    try {
      await onDeleteSuccess();
      setPreviewUrl(null);
      setSelectedFile(null);
      setSuccessMessage('Asset deleted successfully.');
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (err) {
      setErrorMessage(err.message || 'Delete failed.');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="w-full max-w-md p-4 bg-white rounded-xl border border-gray-200 shadow-sm">
      <label className="block text-sm font-semibold text-gray-700 mb-2">{label}</label>

      {/* Drag and drop zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !disabled && fileInputRef.current?.click()}
        className={`relative flex flex-col items-center justify-center p-6 border-2 border-dashed rounded-lg cursor-pointer transition-colors ${
          isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:bg-gray-50'
        } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept={accept}
          onChange={handleFileChange}
          disabled={disabled || isUploading}
          className="hidden"
        />

        {previewUrl ? (
          <div className="relative group w-32 h-32 rounded-lg overflow-hidden border border-gray-200">
            <img src={previewUrl} alt="Preview" className="w-full h-full object-cover" />
            <div className="absolute inset-0 bg-black bg-opacity-40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
              <span className="text-white text-xs font-medium">Click to change</span>
            </div>
          </div>
        ) : (
          <div className="text-center">
            <svg className="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
              <path
                d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            <p className="mt-1 text-sm text-gray-600">
              <span className="font-semibold text-blue-600">Click to upload</span> or drag and drop
            </p>
            <p className="text-xs text-gray-500">Max size: {maxSizeMB}MB</p>
          </div>
        )}

        {selectedFile && (
          <p className="mt-2 text-xs font-medium text-gray-700 truncate max-w-full">
            Selected: {selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} KB)
          </p>
        )}
      </div>

      {/* Action Buttons */}
      <div className="mt-4 flex gap-2 justify-end">
        {allowDelete && (previewUrl || currentImageUrl) && (
          <button
            type="button"
            onClick={handleDelete}
            disabled={disabled || isUploading}
            className="px-3 py-1.5 text-xs font-medium text-red-600 bg-red-50 hover:bg-red-100 rounded-md transition"
          >
            Remove
          </button>
        )}

        {selectedFile && (
          <button
            type="button"
            onClick={handleUpload}
            disabled={disabled || isUploading}
            className="px-4 py-1.5 text-xs font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md transition flex items-center gap-1.5"
          >
            {isUploading && (
              <svg className="animate-spin h-3.5 w-3.5 text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
              </svg>
            )}
            {isUploading ? 'Uploading...' : 'Upload'}
          </button>
        )}
      </div>

      {/* Status Alerts */}
      {errorMessage && (
        <div className="mt-3 p-2.5 bg-red-50 border border-red-200 text-red-700 text-xs rounded-md">
          {errorMessage}
        </div>
      )}

      {successMessage && (
        <div className="mt-3 p-2.5 bg-green-50 border border-green-200 text-green-700 text-xs rounded-md">
          {successMessage}
        </div>
      )}
    </div>
  );
}
