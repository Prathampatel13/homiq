import api from './axios';
import { LocationStreamUpdate, TechnicianProfile } from '../types';

export interface GeocodeResult {
  latitude: number;
  longitude: number;
  formatted_address: string;
  city?: string;
  state?: string;
  pincode?: string;
}

export interface EtaResult {
  distance_km: number;
  duration_minutes: number;
  eta_timestamp: string;
}

export const mapsApi = {
  geocode: async (address: string): Promise<GeocodeResult> => {
    const response = await api.get<GeocodeResult>(`/maps/geocode?address=${encodeURIComponent(address)}`);
    return response.data;
  },

  reverseGeocode: async (latitude: number, longitude: number): Promise<GeocodeResult> => {
    const response = await api.get<GeocodeResult>(`/maps/reverse-geocode?latitude=${latitude}&longitude=${longitude}`);
    return response.data;
  },

  getEta: async (origin_lat: number, origin_lng: number, dest_lat: number, dest_lng: number): Promise<EtaResult> => {
    const response = await api.get<EtaResult>(
      `/maps/eta?origin_lat=${origin_lat}&origin_lng=${origin_lng}&dest_lat=${dest_lat}&dest_lng=${dest_lng}`
    );
    return response.data;
  },

  getNearbyTechnicians: async (latitude: number, longitude: number, radius_km: number = 25): Promise<TechnicianProfile[]> => {
    const response = await api.get<TechnicianProfile[]>(
      `/maps/nearby-technicians?latitude=${latitude}&longitude=${longitude}&radius_km=${radius_km}`
    );
    return response.data;
  },

  updateLocation: async (data: {
    booking_id?: number;
    latitude: number;
    longitude: number;
    speed?: number;
    heading?: number;
    eta_minutes?: number;
  }): Promise<{ message: string }> => {
    const response = await api.post<{ message: string }>('/location/update', data);
    return response.data;
  },

  getCurrentLocation: async (): Promise<LocationStreamUpdate> => {
    const response = await api.get<LocationStreamUpdate>('/location/current');
    return response.data;
  },

  getBookingLocation: async (bookingId: number): Promise<LocationStreamUpdate> => {
    const response = await api.get<LocationStreamUpdate>(`/location/booking/${bookingId}`);
    return response.data;
  },
};
