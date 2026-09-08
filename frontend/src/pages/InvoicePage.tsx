import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { invoicesApi } from '../api/invoices';
import { bookingsApi } from '../api/bookings';
import { Invoice, Booking } from '../types';
import { ArrowLeft, Printer, Download, CheckCircle2 } from 'lucide-react';
import { PageContainer } from '../components/common/PageContainer';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';

export const InvoicePage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [invoice, setInvoice] = useState<Invoice | null>(null);
  const [booking, setBooking] = useState<Booking | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchInvoice = async () => {
      try {
        if (!id) return;
        const invData = await invoicesApi.getInvoice(Number(id));
        setInvoice(invData);
        
        if (invData.booking_id) {
          const bData = await bookingsApi.getBooking(invData.booking_id);
          setBooking(bData);
        }
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load invoice');
      } finally {
        setLoading(false);
      }
    };
    fetchInvoice();
  }, [id]);

  if (loading) return <PageContainer><LoadingSpinner center /></PageContainer>;
  if (error || !invoice) {
    return (
      <PageContainer>
        <div className="flex flex-col items-center justify-center min-h-[50vh]">
          <h2 className="text-xl text-red-400 mb-2">Invoice Not Found</h2>
          <p className="text-slate-400 mb-4">{error}</p>
          <button onClick={() => navigate(-1)} className="btn-secondary px-4 py-2 text-sm">
            Go Back
          </button>
        </div>
      </PageContainer>
    );
  }

  const handlePrint = () => {
    window.print();
  };

  return (
    <PageContainer>
      {/* Non-printable header */}
      <div className="flex items-center justify-between mb-6 print:hidden">
        <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors">
          <ArrowLeft className="w-5 h-5" />
          <span>Back</span>
        </button>
        <div className="flex gap-3">
          <button onClick={handlePrint} className="px-4 py-2 bg-dark-850 hover:bg-dark-800 text-slate-300 rounded-lg flex items-center gap-2 transition-colors border border-dark-750">
            <Printer className="w-4 h-4" />
            <span>Print</span>
          </button>
        </div>
      </div>

      {/* Printable Invoice Area */}
      <div className="bg-white text-slate-900 p-8 md:p-12 rounded-xl shadow-lg max-w-4xl mx-auto print:shadow-none print:p-0">
        
        {/* Header */}
        <div className="flex justify-between items-start border-b border-slate-200 pb-8 mb-8">
          <div>
            <h1 className="text-3xl font-black text-emerald-600 mb-1 tracking-tight">HomiQ</h1>
            <p className="text-slate-500 font-medium text-sm tracking-widest uppercase">Digital Tax Invoice</p>
          </div>
          <div className="text-right">
            <h2 className="text-xl font-bold text-slate-800 mb-1">#{invoice.invoice_number}</h2>
            <div className="flex items-center justify-end gap-2 text-sm">
              <span className="text-slate-500">Status:</span>
              {invoice.status === 'paid' ? (
                <span className="flex items-center gap-1 text-emerald-600 font-semibold bg-emerald-50 px-2 py-0.5 rounded">
                  <CheckCircle2 className="w-4 h-4" /> Paid
                </span>
              ) : (
                <span className="text-amber-600 font-semibold uppercase">{invoice.status}</span>
              )}
            </div>
            <p className="text-slate-500 text-sm mt-2">
              Date: {new Date(invoice.created_at).toLocaleDateString()}
            </p>
          </div>
        </div>

        {/* Addresses */}
        <div className="grid grid-cols-2 gap-8 mb-8">
          <div>
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Billed To</h3>
            <p className="font-bold text-slate-800">{booking?.customer?.full_name || 'Customer'}</p>
            {booking?.service_address && (
              <p className="text-slate-600 text-sm whitespace-pre-wrap mt-1">
                {booking.service_address}
              </p>
            )}
          </div>
          <div className="text-right">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Service Provider</h3>
            <p className="font-bold text-slate-800">HomiQ Services Ltd.</p>
            <p className="text-slate-600 text-sm mt-1">
              contact@homiq.com<br />
              +91 (800) 123-4567<br />
              GSTIN: 27AABCU9603R1ZN
            </p>
          </div>
        </div>

        {/* Line Items */}
        <div className="mb-8">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b-2 border-slate-800 text-slate-800">
                <th className="py-3 px-2 font-bold text-sm">Description</th>
                <th className="py-3 px-2 font-bold text-sm text-right w-32">Amount</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-slate-200">
                <td className="py-4 px-2">
                  <p className="font-semibold text-slate-800">{booking?.service?.title || 'Home Service'}</p>
                  <p className="text-sm text-slate-500 mt-1">Booking Ref: #{booking?.booking_number || booking?.id}</p>
                  {booking?.scheduled_time && (
                    <p className="text-sm text-slate-500">Service Date: {new Date(booking.scheduled_time).toLocaleDateString()}</p>
                  )}
                </td>
                <td className="py-4 px-2 text-right font-medium text-slate-800">
                  ₹{invoice.subtotal.toFixed(2)}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        {/* Totals */}
        <div className="flex justify-end mb-12">
          <div className="w-64 space-y-3">
            <div className="flex justify-between text-sm text-slate-600">
              <span>Subtotal</span>
              <span>₹{invoice.subtotal.toFixed(2)}</span>
            </div>
            {invoice.discount_amount > 0 && (
              <div className="flex justify-between text-sm text-emerald-600">
                <span>Discount</span>
                <span>-₹{invoice.discount_amount.toFixed(2)}</span>
              </div>
            )}
            <div className="flex justify-between text-sm text-slate-600 border-b border-slate-200 pb-3">
              <span>Tax ({invoice.tax_percentage}%)</span>
              <span>₹{invoice.tax_amount.toFixed(2)}</span>
            </div>
            <div className="flex justify-between text-lg font-black text-slate-900 pt-1">
              <span>Total</span>
              <span>₹{invoice.total_amount.toFixed(2)}</span>
            </div>
            
            {invoice.status === 'paid' && (
              <div className="mt-4 pt-4 border-t border-slate-200">
                <div className="flex justify-between text-sm text-emerald-600 font-bold">
                  <span>Amount Paid</span>
                  <span>₹{invoice.amount_paid.toFixed(2)}</span>
                </div>
                <div className="text-right text-xs text-slate-500 mt-1">
                  Paid on {invoice.paid_at ? new Date(invoice.paid_at).toLocaleDateString() : new Date(invoice.updated_at).toLocaleDateString()}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="border-t border-slate-200 pt-8 text-center text-sm text-slate-500">
          <p className="font-medium text-slate-700 mb-1">Thank you for choosing HomiQ Services!</p>
          <p>If you have any questions concerning this invoice, please contact support.</p>
          <p className="mt-4 text-xs text-slate-400 uppercase tracking-widest">This is a computer generated invoice and does not require a physical signature.</p>
        </div>
      </div>
    </PageContainer>
  );
};

export default InvoicePage;
