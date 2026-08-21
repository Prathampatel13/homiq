import React, { useState } from 'react';
import { MapPin, X, AlertCircle, Loader2 } from 'lucide-react';
import { customerApi } from '../../api/customer';
import { CustomerAddress } from '../../types';

export interface AddressModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSaved: (address: CustomerAddress) => void;
  initialData?: CustomerAddress | null;
}

export const AddressModal: React.FC<AddressModalProps> = ({
  isOpen,
  onClose,
  onSaved,
  initialData,
}) => {
  const [fullName, setFullName] = useState(initialData?.full_name || 'Resident');
  const [phone, setPhone] = useState(initialData?.phone || '+91 98765 43210');
  const [houseNo, setHouseNo] = useState(initialData?.house_no || '');
  const [building, setBuilding] = useState(initialData?.building || '');
  const [area, setArea] = useState(initialData?.area || '');
  const [city, setCity] = useState(initialData?.city || '');
  const [stateName, setStateName] = useState(initialData?.state || 'State');
  const [pincode, setPincode] = useState(initialData?.pincode || '');
  const [isDefault, setIsDefault] = useState(initialData?.is_default || false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!houseNo.trim() || !area.trim() || !city.trim() || !pincode.trim()) {
      setError('Please provide house/unit no, area, city, and pincode.');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const payload = {
        full_name: fullName,
        phone: phone,
        house_no: houseNo,
        building: building || undefined,
        area: area,
        city: city,
        state: stateName || 'State',
        pincode: pincode,
        is_default: isDefault,
      };

      let saved: CustomerAddress;
      if (initialData?.id) {
        saved = await customerApi.updateAddress(initialData.id, payload);
      } else {
        saved = await customerApi.createAddress(payload);
      }

      onSaved(saved);
      onClose();
    } catch (err: any) {
      console.error('Failed to save address:', err);
      setError(err?.response?.data?.detail || 'Failed to save address. Please check your entries.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-dark-950/85 backdrop-blur-md animate-in fade-in duration-150">
      <div className="relative w-full max-w-lg rounded-3xl bg-dark-900 border border-dark-750 p-6 sm:p-8 shadow-modal text-white">
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-2 rounded-xl bg-dark-850 hover:bg-dark-800 text-slate-400 hover:text-white border border-dark-750 transition-colors"
        >
          <X className="w-4 h-4" />
        </button>

        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-sage-400/15 border border-sage-400/30 flex items-center justify-center text-sage-400 shrink-0">
            <MapPin className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white tracking-tight">
              {initialData ? 'Edit Residence Address' : 'Add Residence Address'}
            </h3>
            <p className="text-xs text-slate-400">Precision dispatch location for service technicians</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">House / Villa No *</label>
              <input
                type="text"
                value={houseNo}
                onChange={(e) => setHouseNo(e.target.value)}
                placeholder="Apt 402 / Villa 12"
                className="input-field"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Building / Society (Optional)</label>
              <input
                type="text"
                value={building}
                onChange={(e) => setBuilding(e.target.value)}
                placeholder="Palm Heights"
                className="input-field"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">Street / Area *</label>
            <input
              type="text"
              value={area}
              onChange={(e) => setArea(e.target.value)}
              placeholder="Outer Ring Road, Sector 4"
              className="input-field"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">City *</label>
              <input
                type="text"
                value={city}
                onChange={(e) => setCity(e.target.value)}
                placeholder="City"
                className="input-field"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Pincode *</label>
              <input
                type="text"
                value={pincode}
                onChange={(e) => setPincode(e.target.value)}
                placeholder="6-digit PIN"
                className="input-field"
                required
              />
            </div>
          </div>

          <div className="flex items-center gap-2 pt-2">
            <input
              type="checkbox"
              id="isDefaultAddr"
              checked={isDefault}
              onChange={(e) => setIsDefault(e.target.checked)}
              className="w-4 h-4 rounded bg-dark-850 border-dark-750 text-sage-400 focus:ring-0"
            />
            <label htmlFor="isDefaultAddr" className="text-xs text-slate-300 cursor-pointer">
              Set as default service address
            </label>
          </div>

          {error && (
            <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div className="pt-4 flex items-center justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="btn-secondary text-xs px-4 py-2.5"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="btn-primary text-xs px-5 py-2.5 flex items-center gap-1.5"
            >
              {loading && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
              <span>Save Address</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
