'use client';

import { useState, useCallback } from 'react';
import axios from 'axios';

interface FileData {
  id: number;
  filename: string;
  original_name: string;
  file_size: number;
  content_type: string;
  created_at: string;
}

export default function Home() {
  const [files, setFiles] = useState<FileData[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [dragActive, setDragActive] = useState(false);

  const API_BASE = 'http://localhost:8000/api/v1';

  const loadFiles = useCallback(async () => {
    try {
      const response = await axios.get(`${API_BASE}/files/`);
      setFiles(response.data.files);
    } catch (error) {
      console.error('Failed to load files:', error);
    }
  }, []);

  const handleFileUpload = useCallback(async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);

    setUploading(true);
    setUploadProgress(0);

    try {
      await axios.post(`${API_BASE}/files/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round(
            ((progressEvent.loaded || 0) * 100) / (progressEvent.total || 1)
          );
          setUploadProgress(progress);
        },
      });

      await loadFiles();
      alert('File uploaded successfully!');
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Upload failed. Please try again.');
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  }, [loadFiles]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileUpload(files[0]);
    }
  }, [handleFileUpload]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
  }, []);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileUpload(files[0]);
    }
  }, [handleFileUpload]);

  const downloadFile = useCallback(async (fileId: number, filename: string) => {
    try {
      const response = await axios.get(`${API_BASE}/files/${fileId}/download`, {
        responseType: 'blob',
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Download failed:', error);
      alert('Download failed. Please try again.');
    }
  }, []);

  const deleteFile = useCallback(async (fileId: number) => {
    if (!confirm('Are you sure you want to delete this file?')) {
      return;
    }

    try {
      await axios.delete(`${API_BASE}/files/${fileId}`);
      await loadFiles();
      alert('File deleted successfully!');
    } catch (error) {
      console.error('Delete failed:', error);
      alert('Delete failed. Please try again.');
    }
  }, [loadFiles]);

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto p-6">
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">📝 Test Writer</h1>
          <p className="text-gray-600">Upload and manage your documents</p>
        </header>

        <main className="space-y-8">
          {/* Upload Section */}
          <section className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-2xl font-semibold mb-4">Upload Document</h2>
            
            <div
              className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                dragActive
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-300 hover:border-gray-400'
              }`}
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
            >
              {uploading ? (
                <div className="space-y-4">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${uploadProgress}%` }}
                    ></div>
                  </div>
                  <p className="text-gray-600">Uploading... {uploadProgress}%</p>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="text-6xl">📁</div>
                  <h3 className="text-lg font-medium">
                    Drop files here or click to browse
                  </h3>
                  <p className="text-gray-500">
                    Supported formats: PDF, DOC, DOCX, TXT, JPG, PNG
                  </p>
                  <p className="text-sm text-gray-400">Maximum file size: 10MB</p>
                  <input
                    type="file"
                    id="fileInput"
                    className="hidden"
                    accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png"
                    onChange={handleFileSelect}
                  />
                  <button
                    onClick={() => document.getElementById('fileInput')?.click()}
                    className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Browse Files
                  </button>
                </div>
              )}
            </div>
          </section>

          {/* Files List Section */}
          <section className="bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-semibold">Your Documents</h2>
              <button
                onClick={loadFiles}
                className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors"
              >
                🔄 Refresh
              </button>
            </div>

            {files.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <div className="text-4xl mb-2">📂</div>
                <p>No files uploaded yet</p>
              </div>
            ) : (
              <div className="grid gap-4">
                {files.map((file) => (
                  <div
                    key={file.id}
                    className="border rounded-lg p-4 hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <h3 className="font-medium text-gray-900">
                          {file.original_name}
                        </h3>
                        <p className="text-sm text-gray-500">
                          {formatFileSize(file.file_size)} • {file.content_type}
                        </p>
                        <p className="text-xs text-gray-400">
                          Uploaded: {formatDate(file.created_at)}
                        </p>
                      </div>
                      <div className="flex space-x-2">
                        <button
                          onClick={() => downloadFile(file.id, file.original_name)}
                          className="bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 transition-colors"
                        >
                          ⬇️ Download
                        </button>
                        <button
                          onClick={() => deleteFile(file.id)}
                          className="bg-red-600 text-white px-3 py-1 rounded hover:bg-red-700 transition-colors"
                        >
                          🗑️ Delete
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>
        </main>
      </div>
    </div>
  );
}
