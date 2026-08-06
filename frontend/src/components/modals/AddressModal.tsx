import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { MapPin, X, Plus } from 'lucide-react';
import { addressApi } from '../../api/address';
import { CustomerAddress } from '../../types';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';

interface AddressModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAddressCreated: (newAddress: CustomerAddress) => void;
}

export const AddressModal: React.FC<AddressModalProps> = ({
  isOpen,
  onClose,
  onAddressCreated,
}) => {
  const [fullName, setFullName] = useState('');
  const [phone, setPhone] = useState('');
  const [houseNo, setHouseNo] = useState('');
  const [area, setArea] = useState('');
  const [city, setCity] = useState('Mumbai');
  const [state, setState] = useState('Maharashtra');
  const [pincode, setPincode] = useState('');
  const [isDefault, setIsDefault] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMessage('');

    try {
      const newAddr = await addressApi.createAddress({
        full_name: fullName,
        phone,
        house_no: houseNo,
        area,
        city,
        state,
        pincode,
        is_default: isDefault,
      });

      onAddressCreated(newAddr);
      onClose();
    } catch (err: any) {
      setErrorMessage(
        err.response?.data?.detail || 'Failed to add address. Please verify details.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4 z-50">
      <motion.div
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.95, opacity: 0 }}
        className="glass-card p-6 max-w-lg w-full space-y-6 relative border-slate-800"
      >
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-brand-500/10 text-brand-400 flex items-center justify-center">
              <MapPin className="w-4 h-4" />
            </div>
            <h3 className="text-lg font-bold text-white">Add Delivery Address</h3>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        {errorMessage && (
          <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs font-medium">
            {errorMessage}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <Input label="Recipient Full Name" value={fullName} onChange={(e) => setFullName(e.target.value)} required placeholder="John Doe" />
            <Input label="Contact Phone" value={phone} onChange={(e) => setPhone(e.target.value)} required placeholder="+91 98765 43210" />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <Input label="House / Flat / Building No." value={houseNo} onChange={(e) => setHouseNo(e.target.value)} required placeholder="Apt 4B, Sky Tower" />
            <Input label="Area / Locality / Landmark" value={area} onChange={(e) => setArea(e.target.value)} required placeholder="Bandra West" />
          </div>

          <div className="grid grid-cols-3 gap-3">
            <Input label="City" value={city} onChange={(e) => setCity(e.target.value)} required />
            <Input label="State" value={state} onChange={(e) => setState(e.target.value)} required />
            <Input label="Pincode" value={pincode} onChange={(e) => setPincode(e.target.value)} required placeholder="400050" />
          </div>

          <div className="flex items-center gap-2 pt-2">
            <input
              type="checkbox"
              id="isDefaultCheck"
              checked={isDefault}
              onChange={(e) => setIsDefault(e.target.checked)}
              className="w-4 h-4 rounded bg-slate-900 border-slate-800 text-brand-500 focus:ring-brand-500"
            />
            <label htmlFor="isDefaultCheck" className="text-xs text-slate-300">
              Set as primary default delivery address
            </label>
          </div>

          <div className="flex gap-3 pt-4 border-t border-slate-800">
            <Button type="button" variant="secondary" size="md" className="w-1/2" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" size="md" isLoading={isLoading} className="w-1/2" leftIcon={<Plus className="w-4 h-4" />}>
              Save Address
            </Button>
          </div>
        </form>
      </motion.div>
    </div>
  );
};
