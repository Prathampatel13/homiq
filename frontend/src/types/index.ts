export enum UserRole {
  CUSTOMER = 'ROLE_CUSTOMER',
  TECHNICIAN = 'ROLE_TECHNICIAN',
  ADMIN = 'ROLE_ADMIN',
  COMPANY = 'ROLE_COMPANY',
}

export type BookingStatus =
  | 'pending'
  | 'assigned'
  | 'accepted'
  | 'on_the_way'
  | 'arrived'
  | 'waiting_qr'
  | 'qr_verified'
  | 'in_progress'
  | 'completed'
  | 'cancelled'
  | 'rejected'
  | string;

export interface User {
  id: number;
  email: string;
  full_name: string;
  phone?: string;
  role: UserRole | string;
  is_active: boolean;
  is_verified?: boolean;
  is_superuser?: boolean;
  avatar_url?: string | null;
  created_at?: string;
}

export interface ServiceCategory {
  id: number;
  name: string;
  description?: string;
  icon?: string;
  is_active: boolean;
  services_count?: number;
  created_at?: string;
}

export interface Service {
  id: number;
  category_id: number;
  category_name?: string;
  name: string;
  description: string;
  base_price?: number;
  price: number;
  duration_minutes: number;
  rating_avg?: number;
  total_reviews?: number;
  image_url?: string | null;
  is_active: boolean;
  created_at?: string;
}

export interface CustomerAddress {
  id: number;
  customer_id?: number;
  full_name: string;
  phone: string;
  house_no: string;
  building?: string;
  landmark?: string;
  area: string;
  city: string;
  state: string;
  pincode: string;
  latitude?: number | null;
  longitude?: number | null;
  is_default: boolean;
  address_type?: string;
  created_at?: string;
}

export interface TechnicianProfile {
  id: number;
  user_id: number;
  specialization: string;
  experience_years: number;
  skills: string[];
  languages: string[];
  working_hours?: string;
  service_radius_km: number;
  rating_avg: number;
  total_reviews: number;
  completed_jobs?: number;
  earnings_total?: number;
  is_verified: boolean;
  availability: boolean;
  is_online: boolean;
  latitude?: number | null;
  longitude?: number | null;
  user?: User;
  created_at?: string;
}

export interface CompanyProfile {
  id: number;
  user_id: number;
  company_name: string;
  industry?: string;
  description?: string;
  website?: string;
  is_verified?: boolean;
  user?: User;
  created_at?: string;
}

export interface BookingStatusLog {
  id: number;
  booking_id: number;
  from_status?: string | null;
  to_status: string;
  changed_by_user_id?: number | null;
  note?: string | null;
  created_at: string;
}

export interface Booking {
  id: number;
  booking_number?: string;
  customer_id: number;
  technician_id?: number | null;
  service_id: number;
  address_id: number;
  status: BookingStatus;
  booking_date: string;
  preferred_time: string;
  base_price?: number;
  estimated_price?: number;
  discount_amount?: number;
  tax_amount?: number;
  final_price?: number;
  total_amount?: number;
  payment_status?: 'pending' | 'paid' | 'failed' | 'refunded' | string;
  customer_note?: string;
  admin_note?: string;
  qr_code?: string;
  verification_token?: string;
  otp_code?: string;
  created_at: string;
  updated_at?: string;
  service?: Service;
  customer?: User;
  technician?: TechnicianProfile | User;
  address?: CustomerAddress;
  logs?: BookingStatusLog[];
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
  service_name?: string;
}

export interface NotificationItem {
  id: number;
  user_id: number;
  title: string;
  message: string;
  notification_type?: string;
  is_read: boolean;
  created_at: string;
}

export interface Payment {
  id: number;
  booking_id: number;
  customer_id?: number;
  amount: number;
  currency: string;
  status: 'pending' | 'captured' | 'failed' | 'refunded' | string;
  payment_method?: string;
  razorpay_order_id?: string;
  razorpay_payment_id?: string;
  created_at: string;
}

export interface Invoice {
  id: number;
  booking_id: number;
  customer_id: number;
  invoice_number: string;
  subtotal: number;
  discount_amount: number;
  tax_percentage: number;
  tax_amount: number;
  total_amount: number;
  amount_paid: number;
  amount_due: number;
  status: 'draft' | 'issued' | 'paid' | 'cancelled' | string;
  notes?: string;
  paid_at?: string | null;
  created_at: string;
}

export interface Coupon {
  id: number;
  code: string;
  discount_type: 'percentage' | 'flat' | string;
  discount_value: number;
  max_discount_amount?: number | null;
  min_order_amount: number;
  usage_limit_per_user?: number;
  valid_from: string;
  valid_until: string;
  is_active: boolean;
  created_at?: string;
}

export interface JobPost {
  id: number;
  company_id?: number;
  title: string;
  description: string;
  requirements?: string;
  location?: string;
  salary_range?: string;
  is_active: boolean;
  created_at: string;
  company?: CompanyProfile;
  applications_count?: number;
}

export interface JobApplication {
  id: number;
  job_id: number;
  job_post_id?: number;
  technician_id: number;
  cover_letter?: string;
  status: 'applied' | 'shortlisted' | 'rejected' | 'hired' | string;
  created_at: string;
  job?: JobPost;
  technician?: TechnicianProfile | User;
}

export interface VerificationStatus {
  booking_id: number;
  current_status: string;
  qr_generated: boolean;
  qr_verified: boolean;
  otp_verified: boolean;
  service_started: boolean;
  is_completed: boolean;
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
  booking_id?: number;
  latitude: number;
  longitude: number;
  speed?: number;
  heading?: number;
  eta_minutes?: number;
  timestamp?: string;
}

export interface AdminSettings {
  commission_percentage: number;
  tax_percentage: number;
  support_email?: string;
  support_phone?: string;
  working_hours?: string;
  updated_at?: string;
}

export interface AnalyticsOverview {
  total_customers?: number;
  total_technicians?: number;
  total_bookings?: number;
  total_revenue?: number;
  customer_growth_rate?: number;
  booking_growth_rate?: number;
  revenue_growth_rate?: number;
  completed_bookings_count?: number;
  active_bookings_count?: number;
}
