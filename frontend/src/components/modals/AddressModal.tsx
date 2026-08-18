import React, { useState, useEffect } from 'react';
import { CustomerAddress } from '../../types';
import { Modal } from '../ui/Modal';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';
import { customerApi } from '../../api/customer';
import { useToast } from '../ui/Toast';
import { extractErrorMessage } from '../../api/axios';

interface AddressModalProps {
  isOpen: boolean;
  onClose: () => void;
  addressToEdit?: CustomerAddress | null;
  onSuccess: (address: CustomerAddress) => void;
}

export const AddressModal: React.FC<AddressModalProps> = ({
  isOpen,
  onClose,
  addressToEdit,
  onSuccess,
}) => {
  const toast = useToast();
  const [isLoading, setIsLoading] = useState(false);

  const [formData, setFormData] = useState({
    full_name: '',
    phone: '',
    house_no: '',
    building: '',
    landmark: '',
    area: '',
    city: '',
    state: '',
    pincode: '',
    is_default: false,
    address_type: 'home',
  });

  useEffect(() => {
    if (addressToEdit) {
      setFormData({
        full_name: addressToEdit.full_name || '',
        phone: addressToEdit.phone || '',
        house_no: addressToEdit.house_no || '',
        building: addressToEdit.building || '',
        landmark: addressToEdit.landmark || '',
        area: addressToEdit.area || '',
        city: addressToEdit.city || '',
        state: addressToEdit.state || '',
        pincode: addressToEdit.pincode || '',
        is_default: addressToEdit.is_default || false,
        address_type: addressToEdit.address_type || 'home',
      });
    } else {
      setFormData({
        full_name: '',
        phone: '',
        house_no: '',
        building: '',
        landmark: '',
        area: '',
        city: '',
        state: '',
        pincode: '',
        is_default: false,
        address_type: 'home',
      });
    }
  }, [addressToEdit, isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.full_name || !formData.phone || !formData.house_no || !formData.area || !formData.city || !formData.state || !formData.pincode) {
      toast.error('Validation Error', 'Please fill in all required address fields.');
      return;
    }

    setIsLoading(true);
    try {
      let savedAddress: CustomerAddress;
      if (addressToEdit) {
        savedAddress = await customerApi.updateAddress(addressToEdit.id, formData);
        toast.success('Address Updated', 'Saved changes to address.');
      } else {
        savedAddress = await customerApi.createAddress(formData);
        toast.success('Address Added', 'New service address created.');
      }
      onSuccess(savedAddress);
      onClose();
    } catch (err) {
      toast.error('Failed to save address', extractErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={addressToEdit ? 'Edit Service Address' : 'Add New Address'}
      description="Service technicians will arrive at this location."
      maxWidth="lg"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Input
            label="Contact Person Full Name *"
            placeholder="e.g. John Doe"
            value={formData.full_name}
            onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
            required
          />
          <Input
            label="Contact Phone Number *"
            placeholder="e.g. +91 98765 43210"
            value={formData.phone}
            onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
            required
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Input
            label="Flat / House / Apt No. *"
            placeholder="e.g. Flat 402"
            value={formData.house_no}
            onChange={(e) => setFormData({ ...formData, house_no: e.target.value })}
            required
          />
          <Input
            label="Building / Society Name"
            placeholder="e.g. Horizon Towers"
            value={formData.building}
            onChange={(e) => setFormData({ ...formData, building: e.target.value })}
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Input
            label="Area / Neighborhood *"
            placeholder="e.g. Indiranagar"
            value={formData.area}
            onChange={(e) => setFormData({ ...formData, area: e.target.value })}
            required
          />
          <Input
            label="Landmark"
            placeholder="e.g. Opposite Metro Station"
            value={formData.landmark}
            onChange={(e) => setFormData({ ...formData, landmark: e.target.value })}
          />
        </div>

        <div className="grid grid-cols-3 gap-3">
          <Input
            label="City *"
            placeholder="e.g. Bengaluru"
            value={formData.city}
            onChange={(e) => setFormData({ ...formData, city: e.target.value })}
            required
          />
          <Input
            label="State *"
            placeholder="e.g. Karnataka"
            value={formData.state}
            onChange={(e) => setFormData({ ...formData, state: e.target.value })}
            required
          />
          <Input
            label="Pincode *"
            placeholder="e.g. 560038"
            value={formData.pincode}
            onChange={(e) => setFormData({ ...formData, pincode: e.target.value })}
            required
          />
        </div>

        <div className="flex items-center gap-2 pt-2">
          <input
            type="checkbox"
            id="is_default"
            checked={formData.is_default}
            onChange={(e) => setFormData({ ...formData, is_default: e.target.checked })}
            className="rounded border-dark-700 bg-dark-800 text-brand-500 focus:ring-brand-500 h-4 w-4"
          />
          <label htmlFor="is_default" className="text-xs text-slate-300 select-none cursor-pointer">
            Set as default service address
          </label>
        </div>

        <div className="flex items-center justify-end gap-3 pt-4 border-t border-dark-750">
          <Button variant="outline" size="sm" type="button" onClick={onClose} disabled={isLoading}>
            Cancel
          </Button>
          <Button variant="primary" size="sm" type="submit" isLoading={isLoading}>
            {addressToEdit ? 'Save Address' : 'Create Address'}
          </Button>
        </div>
      </form>
    </Modal>
  );
};
