import React, { useState, useEffect } from 'react';
import { Camera, FileText, Image as ImageIcon, Plus, Loader2 } from 'lucide-react';
import { mediaApi, MediaAssetResponse, MediaAssetType } from '../../api/media';
import { MediaUploader } from './MediaUploader';
import { MediaLightbox } from './MediaLightbox';
import { useAuthStore } from '../../store/useAuthStore';
import { UserRole } from '../../types';

interface BookingMediaSectionProps {
  bookingId: number;
  assignedTechnicianId?: number;
}

export const BookingMediaSection: React.FC<BookingMediaSectionProps> = ({ 
  bookingId,
  assignedTechnicianId
}) => {
  const { user, getEffectiveRole } = useAuthStore();
  const isTechnician = getEffectiveRole() === UserRole.TECHNICIAN;
  const canUpload = isTechnician && user?.id === assignedTechnicianId;

  const [media, setMedia] = useState<MediaAssetResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeUploader, setActiveUploader] = useState<MediaAssetType | null>(null);
  
  const [lightboxData, setLightboxData] = useState<{
    images: MediaAssetResponse[];
    index: number;
  } | null>(null);
  
  const [invoice, setInvoice] = useState<any>(null);

  const fetchMedia = async () => {
    try {
      setIsLoading(true);
      const res = await mediaApi.getOwnerMedia('booking', bookingId);
      setMedia(res.items);
      
      try {
        const { invoicesApi } = await import('../../api/invoices');
        const invRes = await invoicesApi.getInvoices();
        const invoices = Array.isArray(invRes) ? invRes : invRes.items;
        const match = invoices.find((inv: any) => inv.booking_id === bookingId);
        if (match) setInvoice(match);
      } catch (err) {
        console.error('Failed to fetch invoice', err);
      }
    } catch (err) {
      console.error('Failed to fetch booking media', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchMedia();
  }, [bookingId]);

  const beforeMedia = media.filter(m => m.asset_type === 'booking_before');
  const afterMedia = media.filter(m => m.asset_type === 'booking_after');
  const docMedia = media.filter(m => m.asset_type === 'booking_attachment');

  const handleUploadSuccess = (newAsset: MediaAssetResponse) => {
    setMedia(prev => [newAsset, ...prev]);
    setActiveUploader(null);
  };

  const renderMediaGroup = (
    title: string, 
    items: MediaAssetResponse[], 
    assetType: MediaAssetType,
    icon: React.ReactNode
  ) => {
    if (activeUploader === assetType) {
      return (
        <div className="col-span-full mb-4">
          <MediaUploader
            bookingId={bookingId}
            assetType={assetType}
            title={`Upload ${title}`}
            onUploadSuccess={handleUploadSuccess}
            onCancel={() => setActiveUploader(null)}
          />
        </div>
      );
    }

    return (
      <div className="p-3 rounded-xl bg-dark-900 border border-dark-750 flex flex-col h-full">
        <div className="flex items-center justify-between mb-2">
          <span className="text-[10px] font-mono text-slate-400 uppercase">{title}</span>
          {canUpload && (
            <button
              onClick={() => setActiveUploader(assetType)}
              className="p-1 rounded bg-dark-800 hover:bg-blue-600/20 hover:text-blue-400 text-slate-400 transition-colors"
            >
              <Plus className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        {items.length > 0 ? (
          <div className="flex-1 flex flex-col gap-2">
            <div className="relative w-full h-20 rounded-lg overflow-hidden border border-dark-750 bg-dark-950 group cursor-pointer"
                 onClick={() => setLightboxData({ images: items, index: 0 })}>
              {items[0].resource_type === 'image' ? (
                <>
                  <img src={items[0].thumbnail_url || items[0].secure_url} alt={title} className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105" />
                  <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                    <span className="text-white text-xs font-semibold">View All</span>
                  </div>
                </>
              ) : (
                <div className="w-full h-full flex flex-col items-center justify-center text-slate-400">
                  <FileText className="w-6 h-6 mb-1" />
                  <span className="text-[10px] font-mono">{items[0].format.toUpperCase()}</span>
                </div>
              )}
              {items.length > 1 && (
                <div className="absolute bottom-1 right-1 px-1.5 py-0.5 rounded bg-black/70 text-white text-[10px] font-mono">
                  +{items.length - 1}
                </div>
              )}
            </div>
            <div className="flex items-center justify-between text-[10px] text-slate-500 font-mono">
              <span>{items.length} file{items.length !== 1 ? 's' : ''}</span>
              <span>{new Date(items[0].created_at).toLocaleDateString()}</span>
            </div>
          </div>
        ) : (
          <div className="flex-1 w-full h-24 rounded-lg bg-dark-850 border border-dashed border-dark-700 flex flex-col items-center justify-center text-slate-500">
            {icon}
            <span className="text-[10px] mt-2">
              {title === 'Invoice / Docs' 
                ? 'No documents uploaded yet.' 
                : `No ${title.toLowerCase().replace(' ', '-')} photos yet.`}
            </span>
            {canUpload && (
              <button
                onClick={() => setActiveUploader(assetType)}
                className="mt-2 text-xs text-blue-400 hover:text-blue-300 transition-colors"
              >
                Upload Now
              </button>
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="p-4 rounded-2xl bg-dark-850 border border-dark-750 space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-[11px] font-mono text-sage-400 uppercase tracking-wider block">
          Site Media & Work Evidence
        </span>
        {isLoading && <Loader2 className="w-3.5 h-3.5 text-sage-400 animate-spin" />}
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 items-stretch">
        {renderMediaGroup('Before Work', beforeMedia, 'booking_before', <Camera className="w-5 h-5 opacity-50" />)}
        {renderMediaGroup('After Work', afterMedia, 'booking_after', <ImageIcon className="w-5 h-5 opacity-50" />)}
        
        <div className="col-span-2 sm:col-span-1 h-full">
          {invoice ? (
            <div className="p-4 rounded-xl bg-dark-900 border border-dark-750 flex flex-col h-full">
              <span className="text-[10px] font-mono text-sage-400 uppercase mb-3">Invoice & Payment</span>
              <div className="flex-1 bg-dark-950 rounded-lg border border-dark-750 p-3 flex flex-col justify-between">
                <div>
                  <div className="flex justify-between items-start mb-2">
                    <span className="text-xs font-bold text-white">#{invoice.invoice_number}</span>
                    <span className={`text-[10px] uppercase font-mono px-1.5 py-0.5 rounded ${
                      invoice.status === 'paid' ? 'bg-sage-400/20 text-sage-400' : 'bg-blue-400/20 text-blue-400'
                    }`}>
                      {invoice.status}
                    </span>
                  </div>
                  <div className="text-[10px] text-slate-400 font-mono mb-0.5">Date: {new Date(invoice.created_at).toLocaleDateString()}</div>
                  <div className="text-[10px] text-slate-400 font-mono mb-2">Total: ₹{invoice.total_amount}</div>
                </div>
                <button 
                  onClick={() => window.open(`/customer/invoices/${invoice.id}`, '_blank')}
                  className="w-full py-1.5 mt-2 bg-dark-800 hover:bg-dark-700 text-xs font-semibold text-white rounded transition-colors border border-dark-700"
                >
                  View Details
                </button>
              </div>
            </div>
          ) : (
            renderMediaGroup('Invoice / Docs', docMedia, 'booking_attachment', <FileText className="w-5 h-5 opacity-50" />)
          )}
        </div>
      </div>

      {lightboxData && (
        <MediaLightbox
          images={lightboxData.images}
          initialIndex={lightboxData.index}
          isOpen={!!lightboxData}
          onClose={() => setLightboxData(null)}
        />
      )}
    </div>
  );
};
