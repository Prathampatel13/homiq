export enum UserRole {
  CUSTOMER = 'ROLE_CUSTOMER',
  TECHNICIAN = 'ROLE_TECHNICIAN',
  ADMIN = 'ROLE_ADMIN',
  COMPANY = 'ROLE_COMPANY',
}

export enum BookingStatus {
  ASSIGNED = 'ASSIGNED',
  ACCEPTED = 'ACCEPTED',
  ON_THE_WAY = 'ON_THE_WAY',
  ARRIVED = 'ARRIVED',
  WAITING_QR = 'WAITING_QR',
  QR_VERIFIED = 'QR_VERIFIED',
  IN_PROGRESS = 'IN_PROGRESS',
  COMPLETED = 'COMPLETED',
  CANCELLED = 'CANCELLED',
}

export interface User {
  id: number;
  email: string;
  full_name: string;
  phone: string;
  role: UserRole;
  is_active: boolean;
  is_verified: boolean;
  avatar_url?: string;
  created_at: string;
}

export interface ServiceCategory {
  id: number;
  name: string;
  description: string;
  icon?: string;
  is_active: boolean;
}

export interface Service {
  id: number;
  category_id: number;
  name: string;
  description: string;
  price: number;
  duration_minutes: number;
  rating_avg: number;
  total_reviews: number;
  image_url?: string;
  is_active: boolean;
}

export interface CustomerAddress {
  id: number;
  customer_id: number;
  full_name: string;
  phone: string;
  house_no: string;
  street_address?: string;
  area: string;
  city: string;
  state: string;
  pincode: string;
  latitude?: number;
  longitude?: number;
  is_default: boolean;
}

export interface Booking {
  id: number;
  booking_number: string;
  customer_id: number;
  technician_id?: number;
  service_id: number;
  address_id: number;
  status: BookingStatus;
  booking_date: string;
  preferred_time: string;
  base_price: number;
  discount_amount: number;
  tax_amount: number;
  final_price: number;
  qr_code?: string;
  special_instructions?: string;
  created_at: string;
  updated_at: string;
  service?: Service;
  customer?: User;
  technician?: User;
  address?: CustomerAddress;
}

export interface Review {
  id: number;
  booking_id: number;
  customer_id: number;
  technician_id: number;
  rating: number;
  comment: string;
  created_at: string;
  customer_name?: string;
}

export interface NotificationItem {
  id: number;
  user_id: number;
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
}

export interface ChatMessage {
  id: string;
  booking_id: number;
  sender_id: number;
  sender_role: string;
  content: string;
  timestamp: string;
}

export interface LocationStreamUpdate {
  technician_id: number;
  booking_id: number;
  latitude: number;
  longitude: number;
  speed?: number;
  heading?: number;
  eta_minutes?: number;
}
