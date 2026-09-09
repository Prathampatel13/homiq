import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { invoicesApi } from '../api/invoices';
import { bookingsApi } from '../api/bookings';
import { Invoice, Booking } from '../types';
import { ArrowLeft, Printer, Download, CheckCircle2 } from 'lucide-react';

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
        setLoading(true);
        const inv = await invoicesApi.getInvoice(Number(id));
        setInvoice(inv);
        if (inv.booking_id) {
          const b = await bookingsApi.getBooking(inv.booking_id);
          setBooking(b);
        }
      } catch (err) {
        setError('Failed to load invoice details');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchInvoice();
  }, [id]);

  if (loading) return <div className="min-h-screen bg-[#F8FAFC] flex items-center justify-center text-slate-700">Loading...</div>;
  if (error || !invoice) {
    return (
      <div className="min-h-screen bg-[#F8FAFC] p-6 md:p-12 text-slate-900">
        <div className="flex flex-col items-center justify-center min-h-[50vh]">
          <h2 className="text-xl font-bold text-rose-600 mb-2">Invoice Not Found</h2>
          <p className="text-slate-600 mb-4">{error}</p>
          <button onClick={() => navigate(-1)} className="btn-secondary px-4 py-2 text-sm">
            Go Back
          </button>
        </div>
      </div>
    );
  }

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] p-4 sm:p-8 text-slate-900">
      {/* Non-printable header */}
      <div className="max-w-4xl mx-auto flex items-center justify-between mb-6 print:hidden">
        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-2 text-slate-600 hover:text-slate-900 transition-colors font-medium"
        >
          <ArrowLeft className="w-4 h-4" />
          <span className="text-sm">Back</span>
        </button>
        <div className="flex items-center gap-3">
          <button
            onClick={handlePrint}
            className="btn-secondary px-4 py-2 text-sm flex items-center gap-2"
          >
            <Printer className="w-4 h-4" />
            <span>Print</span>
          </button>
          <button
            onClick={handlePrint}
            className="btn-primary px-4 py-2 text-sm flex items-center gap-2"
          >
            <Download className="w-4 h-4" />
            <span>Download PDF</span>
          </button>
        </div>
      </div>

      {/* Printable Invoice Container */}
      <div className="max-w-4xl mx-auto bg-white rounded-2xl print:rounded-none shadow-2xl print:shadow-none overflow-hidden print:p-0">
        
        {/* Header Ribbon */}
        <div className="h-4 w-full bg-sage-500 print:bg-slate-800" />
        
        <div className="p-8 sm:p-12">
          {/* Top Section */}
          <div className="flex justify-between items-start mb-12">
            <div>
              <h1 className="text-4xl font-black text-slate-900 tracking-tighter uppercase">INVOICE</h1>
              <p className="text-slate-500 font-mono mt-2">#{invoice.invoice_number}</p>
            </div>
            <div className="text-right">
              {invoice.status === 'paid' ? (
                <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded bg-emerald-100 text-emerald-700 font-bold text-sm">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>PAID</span>
                </div>
              ) : (
                <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded bg-amber-100 text-amber-700 font-bold text-sm">
                  <span>PENDING</span>
                </div>
              )}
              <p className="text-slate-500 text-sm mt-3">
                Date: {new Date(invoice.created_at).toLocaleDateString()}
              </p>
            </div>
          </div>

          {/* Addresses */}
          <div className="grid grid-cols-2 gap-8 mb-8">
            <div>
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Billed To</h3>
              <p className="font-bold text-slate-800">{booking?.customer?.full_name || 'Customer'}</p>
              <p className="text-slate-600 text-sm whitespace-pre-wrap mt-1">
                {booking?.address_id ? 'Address on file' : ''}
              </p>
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
                    <p className="font-semibold text-slate-800">{booking?.service?.name || 'Home Service'}</p>
                    <p className="text-sm text-slate-500 mt-1">Booking Ref: #{booking?.booking_number || booking?.id}</p>
                    {booking?.booking_date && (
                      <p className="text-sm text-slate-500">Service Date: {new Date(booking.booking_date).toLocaleDateString()}</p>
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
                    Paid on {invoice.paid_at ? new Date(invoice.paid_at).toLocaleDateString() : new Date(invoice.created_at).toLocaleDateString()}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Footer */}
          <div className="border-t border-slate-200 pt-8 text-center text-slate-500 text-sm">
            <p className="font-semibold text-slate-700 mb-1">Thank you for choosing HomiQ.</p>
            <p>This is a computer-generated document and does not require a signature.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InvoicePage;
