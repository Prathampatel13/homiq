import React, { useState, useEffect } from 'react';
import { X, ChevronLeft, ChevronRight } from 'lucide-react';
import { MediaAssetResponse } from '../../api/media';

export interface MediaLightboxProps {
  images: MediaAssetResponse[];
  initialIndex: number;
  isOpen: boolean;
  onClose: () => void;
}

export const MediaLightbox: React.FC<MediaLightboxProps> = ({
  images,
  initialIndex,
  isOpen,
  onClose,
}) => {
  const [currentIndex, setCurrentIndex] = useState(initialIndex);

  useEffect(() => {
    setCurrentIndex(initialIndex);
  }, [initialIndex]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return;
      if (e.key === 'Escape') onClose();
      if (e.key === 'ArrowLeft') handlePrev();
      if (e.key === 'ArrowRight') handleNext();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, currentIndex]);

  if (!isOpen || images.length === 0) return null;

  const handlePrev = () => {
    setCurrentIndex((prev) => (prev > 0 ? prev - 1 : images.length - 1));
  };

  const handleNext = () => {
    setCurrentIndex((prev) => (prev < images.length - 1 ? prev + 1 : 0));
  };

  const currentImage = images[currentIndex];

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/95 backdrop-blur-sm animate-in fade-in duration-200">
      <button
        onClick={onClose}
        className="absolute top-6 right-6 p-2 rounded-full bg-white/10 hover:bg-white/20 text-white transition-colors"
      >
        <X className="w-6 h-6" />
      </button>

      {images.length > 1 && (
        <>
          <button
            onClick={handlePrev}
            className="absolute left-6 top-1/2 -translate-y-1/2 p-3 rounded-full bg-white/10 hover:bg-white/20 text-white transition-colors"
          >
            <ChevronLeft className="w-8 h-8" />
          </button>
          <button
            onClick={handleNext}
            className="absolute right-6 top-1/2 -translate-y-1/2 p-3 rounded-full bg-white/10 hover:bg-white/20 text-white transition-colors"
          >
            <ChevronRight className="w-8 h-8" />
          </button>
        </>
      )}

      <div className="relative w-full max-w-5xl max-h-[85vh] flex items-center justify-center p-4">
        {currentImage.resource_type === 'image' ? (
          <img
            src={currentImage.secure_url}
            alt="Work Evidence"
            className="max-w-full max-h-full object-contain rounded-lg shadow-2xl"
          />
        ) : (
          <div className="w-full h-96 flex flex-col items-center justify-center bg-dark-800 rounded-lg">
            <span className="text-white mb-4">Document: {currentImage.format.toUpperCase()}</span>
            <a
              href={currentImage.secure_url}
              target="_blank"
              rel="noopener noreferrer"
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
            >
              View Document
            </a>
          </div>
        )}
      </div>

      <div className="absolute bottom-6 left-1/2 -translate-x-1/2 px-4 py-2 rounded-full bg-black/50 text-white text-sm font-mono tracking-wider">
        {currentIndex + 1} / {images.length}
      </div>
    </div>
  );
};
