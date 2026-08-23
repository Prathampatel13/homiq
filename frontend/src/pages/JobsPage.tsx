import React, { useEffect, useState } from 'react';
import { 
  Briefcase, 
  MapPin, 
  Clock, 
  DollarSign, 
  ChevronRight, 
  CheckCircle2, 
  Building2, 
  Search, 
  Filter,
  X,
  Loader2,
  AlertCircle
} from 'lucide-react';
import { jobsApi } from '../api/jobs';
import { JobPost, JobApplication } from '../types';
import { EmptyState } from '../components/ui/EmptyState';
import { LoadingState } from '../components/ui/LoadingState';
import { useAuthStore } from '../store/useAuthStore';

export const JobsPage: React.FC = () => {
  const { user, isAuthenticated } = useAuthStore();
  const [jobs, setJobs] = useState<JobPost[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  // Application modal
  const [selectedJob, setSelectedJob] = useState<JobPost | null>(null);
  const [coverNote, setCoverNote] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [appliedSuccess, setAppliedSuccess] = useState(false);
  const [applyError, setApplyError] = useState<string | null>(null);

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        setLoading(true);
        const res = await jobsApi.getJobs({});
        const items = Array.isArray(res) ? res : (res as any)?.items || [];
        setJobs(items);
      } catch (err) {
        console.error('Failed to load recruitment jobs:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchJobs();
  }, []);

  const handleApply = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedJob) return;

    try {
      setSubmitting(true);
      setApplyError(null);
      await jobsApi.applyJob(selectedJob.id, coverNote);

      setAppliedSuccess(true);
      setTimeout(() => {
        setAppliedSuccess(false);
        setSelectedJob(null);
        setCoverNote('');
      }, 1800);
    } catch (err: any) {
      console.error('Application failed:', err);
      setApplyError(err?.response?.data?.detail || 'Application submission failed. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const filteredJobs = jobs.filter((j) => {
    const matchQuery = !searchQuery || j.title.toLowerCase().includes(searchQuery.toLowerCase()) || (j.description && j.description.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchQuery;
  });

  return (
    <div className="min-h-screen bg-dark-950 py-12 text-white selection:bg-sage-400/20 selection:text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
        {/* Header */}
        <div className="max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-dark-850 border border-dark-750 mb-3">
            <Briefcase className="w-3.5 h-3.5 text-sage-400" />
            <span className="text-xs font-mono tracking-wider text-slate-300 uppercase">PROFESSIONAL RECRUITMENT</span>
          </div>
          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-white">
            BUILD YOUR CAREER WITH HOMIQ.
          </h1>
          <p className="text-sm text-slate-400 mt-2 leading-relaxed">
            Join the most advanced digital network of master technicians and enterprise fleets. Transparent dispatch, direct bank payouts, and comprehensive insurance backing.
          </p>
        </div>

        {/* Search & Filter Controls */}
        <div className="p-4 rounded-3xl bg-dark-900 border border-dark-750 flex flex-col md:flex-row gap-4 items-center justify-between shadow-card">
          <div className="relative w-full md:w-80">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by trade or title..."
              className="input-field pl-10 text-xs py-2.5"
            />
          </div>

          <div className="flex items-center gap-2 w-full md:w-auto overflow-x-auto pb-2 md:pb-0 scrollbar-none">
            <span className="text-xs font-mono text-slate-400">Showing {filteredJobs.length} active positions</span>
          </div>
        </div>

        {/* Job Listings Grid */}
        {loading ? (
          <LoadingState message="Loading Career Opportunities..." />
        ) : filteredJobs.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredJobs.map((job) => (
              <div
                key={job.id}
                onClick={() => setSelectedJob(job)}
                className="p-6 rounded-3xl bg-dark-900/90 hover:bg-dark-850 border border-dark-750 hover:border-dark-700 transition-all duration-200 cursor-pointer flex flex-col justify-between shadow-card group"
              >
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-[10px] font-mono uppercase px-2.5 py-1 rounded-lg bg-dark-800 text-sage-300 border border-dark-750">
                      Verified Role
                    </span>
                    <span className="text-xs font-mono font-bold text-white">
                      {job.salary_range || 'Competitive Compensation'}
                    </span>
                  </div>

                  <h3 className="text-base font-bold text-white tracking-tight group-hover:text-sage-300 transition-colors mb-2">
                    {job.title}
                  </h3>

                  <p className="text-xs text-slate-400 leading-relaxed line-clamp-3 mb-4">
                    {job.description || 'Master technician role delivering architectural home repairs with SmartVerify standards.'}
                  </p>

                  <div className="space-y-1.5 text-xs text-slate-400 font-mono">
                    <div className="flex items-center gap-1.5">
                      <MapPin className="w-3.5 h-3.5 text-slate-500" />
                      <span>{job.location || 'Metro Hub & Regional Fleet'}</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <Building2 className="w-3.5 h-3.5 text-slate-500" />
                      <span>{job.company?.company_name || 'HomiQ Direct Fleet'}</span>
                    </div>
                  </div>
                </div>

                <div className="pt-5 mt-5 border-t border-dark-750 flex items-center justify-between text-xs text-sage-400 font-semibold">
                  <span>View & Apply</span>
                  <ChevronRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            ))}
          </div>
        ) : (
          <EmptyState
            title="NO CURRENT OPENINGS FOUND"
            description="Try changing your search parameters or check back soon as enterprise fleets expand."
            actionLabel="Reset Search"
            onAction={() => {
              setSearchQuery('');
            }}
          />
        )}
      </div>

      {/* Application Modal */}
      {selectedJob && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-dark-950/85 backdrop-blur-md animate-in fade-in duration-150">
          <div className="relative w-full max-w-lg rounded-3xl bg-dark-900 border border-dark-750 p-6 sm:p-8 shadow-modal text-white">
            <button
              onClick={() => setSelectedJob(null)}
              className="absolute top-5 right-5 p-2 rounded-xl bg-dark-850 hover:bg-dark-800 text-slate-400 hover:text-white border border-dark-750"
            >
              <X className="w-4 h-4" />
            </button>

            {appliedSuccess ? (
              <div className="py-8 text-center space-y-3">
                <div className="w-14 h-14 rounded-full bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400 mx-auto">
                  <CheckCircle2 className="w-7 h-7" />
                </div>
                <h4 className="text-base font-bold text-white">Application Submitted</h4>
                <p className="text-xs text-slate-400">Our enterprise recruitment dispatch team will review your credentials within 24 hours.</p>
              </div>
            ) : (
              <form onSubmit={handleApply} className="space-y-4">
                <div>
                  <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-dark-800 text-sage-300 border border-dark-750">
                    Active Opening
                  </span>
                  <h3 className="text-lg font-bold text-white mt-2">{selectedJob.title}</h3>
                  <p className="text-xs text-slate-400 mt-1">{selectedJob.description}</p>
                </div>

                <div className="p-4 rounded-2xl bg-dark-850 border border-dark-750 space-y-3">
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1">Trade Credentials & Experience Note</label>
                    <textarea
                      value={coverNote}
                      onChange={(e) => setCoverNote(e.target.value)}
                      placeholder="Detail your trade licenses, years of experience, certifications, and preferred operating zones..."
                      rows={4}
                      className="input-field resize-none"
                      required
                    />
                  </div>
                </div>

                {applyError && (
                  <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 shrink-0" />
                    <span>{applyError}</span>
                  </div>
                )}

                <div className="pt-2 flex items-center justify-end gap-3">
                  <button
                    type="button"
                    onClick={() => setSelectedJob(null)}
                    className="btn-secondary text-xs px-4 py-2.5"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={submitting}
                    className="btn-primary text-xs px-6 py-2.5 font-semibold flex items-center gap-1.5"
                  >
                    {submitting && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                    <span>Submit Application</span>
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
