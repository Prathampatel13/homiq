import React, { useState, useRef } from 'react';
import { Upload, X, Loader2, ImagePlus, CheckCircle2, AlertCircle } from 'lucide-react';
import { mediaApi, MediaAssetType, MediaAssetResponse } from '../../api/media';

interface MediaUploaderProps {
  bookingId: number;
  assetType: MediaAssetType;
  title: string;
  onUploadSuccess: (asset: MediaAssetResponse) => void;
  onCancel: () => void;
}

export const MediaUploader: React.FC<MediaUploaderProps> = ({
  bookingId,
  assetType,
  title,
  onUploadSuccess,
  onCancel,
}) => {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [previewUrls, setPreviewUrls] = useState<string[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files);
      const validFiles = files.filter(f => f.size <= 10 * 1024 * 1024); // 10MB limit

      if (validFiles.length !== files.length) {
        setError('Some files were ignored because they exceed the 10MB limit.');
      } else {
        setError(null);
      }

      setSelectedFiles(prev => [...prev, ...validFiles]);
      
      const newUrls = validFiles.map(f => URL.createObjectURL(f));
      setPreviewUrls(prev => [...prev, ...newUrls]);
    }
  };

  const removeFile = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
    setPreviewUrls(prev => {
      const urls = [...prev];
      URL.revokeObjectURL(urls[index]);
      urls.splice(index, 1);
      return urls;
    });
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) return;
    
    setIsUploading(true);
    setError(null);
    
    try {
      const uploadPromises = selectedFiles.map(file => 
        mediaApi.uploadMedia({
          file,
          asset_type: assetType,
          owner_id: bookingId,
          owner_type: 'booking'
        })
      );
      
      const results = await Promise.all(uploadPromises);
      results.forEach(asset => onUploadSuccess(asset));
      
      setSelectedFiles([]);
      setPreviewUrls([]);
    } catch (err: any) {
      console.error('Upload failed:', err);
      setError(err?.response?.data?.detail || 'Failed to upload media. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="p-4 rounded-2xl bg-dark-900 border border-dark-750 animate-in fade-in zoom-in-95 duration-150">
      <div className="flex items-center justify-between mb-4">
        <h4 className="text-sm font-bold text-white tracking-tight">{title}</h4>
        <button onClick={onCancel} className="text-slate-400 hover:text-white transition-colors">
          <X className="w-4 h-4" />
        </button>
      </div>

      {error && (
        <div className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-start gap-2">
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {selectedFiles.length > 0 ? (
        <div className="space-y-4">
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {previewUrls.map((url, i) => (
              <div key={i} className="relative aspect-square rounded-xl overflow-hidden border border-dark-700 bg-dark-950 group">
                <img src={url} alt="Preview" className="w-full h-full object-cover" />
                <button
                  onClick={() => removeFile(i)}
                  disabled={isUploading}
                  className="absolute top-2 right-2 p-1.5 rounded-full bg-black/60 text-white opacity-0 group-hover:opacity-100 transition-opacity hover:bg-rose-500"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={isUploading}
              className="aspect-square rounded-xl border border-dashed border-dark-600 bg-dark-850 hover:bg-dark-800 flex flex-col items-center justify-center gap-2 text-slate-400 hover:text-white transition-colors"
            >
              <ImagePlus className="w-6 h-6" />
              <span className="text-[10px] uppercase tracking-wider font-mono">Add More</span>
            </button>
          </div>
          
          <div className="flex items-center justify-end gap-3 pt-4 border-t border-dark-750">
            <button
              onClick={onCancel}
              disabled={isUploading}
              className="px-4 py-2 text-xs font-semibold text-slate-300 hover:text-white transition-colors disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              onClick={handleUpload}
              disabled={isUploading}
              className="btn-primary text-xs px-5 py-2 flex items-center gap-2 shadow-subtle hover:shadow-metallic disabled:opacity-50"
            >
              {isUploading ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Uploading...</span>
                </>
              ) : (
                <>
                  <Upload className="w-3.5 h-3.5" />
                  <span>Upload {selectedFiles.length} File{selectedFiles.length !== 1 ? 's' : ''}</span>
                </>
              )}
            </button>
          </div>
        </div>
      ) : (
        <div 
          onClick={() => fileInputRef.current?.click()}
          className="w-full h-32 rounded-xl border-2 border-dashed border-dark-700 bg-dark-850 hover:bg-dark-800 hover:border-dark-600 cursor-pointer flex flex-col items-center justify-center gap-3 transition-colors group"
        >
          <div className="w-10 h-10 rounded-full bg-blue-500/10 text-blue-400 flex items-center justify-center group-hover:scale-110 transition-transform">
            <ImagePlus className="w-5 h-5" />
          </div>
          <div className="text-center">
            <p className="text-xs font-semibold text-white">Click to select files</p>
            <p className="text-[10px] text-slate-400 mt-1">JPG, PNG up to 10MB</p>
          </div>
        </div>
      )}

      <input
        type="file"
        ref={fileInputRef}
        className="hidden"
        accept="image/jpeg,image/png,image/webp,application/pdf"
        multiple
        onChange={handleFileSelect}
      />
    </div>
  );
};
