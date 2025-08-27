import React, { useState, useCallback, useRef } from 'react';

interface FileUploadProps {
  acceptedFileTypes: string;
  onFileSelect: (file: File) => void;
}

const FileUpload: React.FC<FileUploadProps> = ({ acceptedFileTypes, onFileSelect }) => {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragEnter = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };
  
  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    
    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      onFileSelect(files[0]);
    }
  }, [onFileSelect]);
  
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      onFileSelect(files[0]);
    }
  };
  
  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const dragClass = isDragging ? 'border-cyan-400 bg-slate-800' : 'border-slate-600 bg-slate-800/50';

  return (
    <div 
      className={`mt-4 p-6 border-2 border-dashed rounded-lg text-center cursor-pointer transition-colors ${dragClass}`}
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
      onClick={handleClick}
    >
      <input 
        ref={fileInputRef}
        type="file" 
        accept={acceptedFileTypes} 
        onChange={handleFileChange}
        className="hidden" 
      />
      <p className="text-slate-400">Drag & drop your file here, or click to select a file.</p>
      <p className="text-xs text-slate-500 mt-1">Supported file type: {acceptedFileTypes}</p>
    </div>
  );
};

export default FileUpload;