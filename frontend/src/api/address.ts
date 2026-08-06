import api from './axios';
import { CustomerAddress } from '../types';

export interface CreateAddressPayload {
  full_name: string;
  phone: string;
  house_no: string;
  street_address?: string;
  area: string;
  city: string;
  state: string;
  pincode: string;
  is_default?: boolean;
}

export const addressApi = {
  createAddress: async (payload: CreateAddressPayload): Promise<CustomerAddress> => {
    const res = await api.post('/customer/addresses', payload);
    return res.data;
  },

  getAddresses: async (): Promise<CustomerAddress[]> => {
    const res = await api.get('/customer/addresses');
    return res.data;
  },

  deleteAddress: async (id: number): Promise<{ success: boolean }> => {
    const res = await api.delete(`/customer/addresses/${id}`);
    return res.data;
  },
};
