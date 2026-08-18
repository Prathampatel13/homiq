import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Briefcase, MapPin, DollarSign, Search, ShieldCheck, ArrowRight, CheckCircle2, User } from 'lucide-react';
import { jobsApi } from '../api/jobs';
import { JobPost } from '../types';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { Modal } from '../components/ui/Modal';
import { Textarea } from '../components/ui/Textarea';
import { LoadingState } from '../components/ui/LoadingState';
import { EmptyState } from '../components/ui/EmptyState';
import { useToast } from '../components/ui/Toast';
import { extractErrorMessage } from '../api/axios';
import { useAuthStore } from '../store/useAuthStore';

export const JobsPage: React.FC = () => {
  const navigate = useNavigate();
  const toast = useToast();
  const { isAuthenticated, user } = useAuthStore();

  const [jobs, setJobs] = useState<JobPost[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  const [selectedJob, setSelectedJob] = useState<JobPost | null>(null);
  const [coverLetter, setCoverLetter] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    jobsApi
      .getJobs()
      .then(setJobs)
      .catch(() => setJobs([]))
      .finally(() => setIsLoading(false));
  }, []);

  const handleApply = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isAuthenticated) {
      toast.info('Authentication Required', 'Please log in as a technician to apply.');
      navigate('/login');
      return;
    }

    if (!selectedJob) return;

    setIsSubmitting(true);
    try {
      await jobsApi.applyJob(selectedJob.id, coverLetter);
      toast.success('Application Submitted!', 'The hiring company has received your application.');
      setSelectedJob(null);
      setCoverLetter('');
    } catch (err) {
      toast.error('Application Failed', extractErrorMessage(err));
    } finally {
      setIsSubmitting(false);
    }
  };

  const filteredJobs = jobs.filter((j) =>
    searchQuery
      ? j.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        j.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (j.location && j.location.toLowerCase().includes(searchQuery.toLowerCase()))
      : true
  );

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-10">
      {/* Header */}
      <div className="text-center max-w-3xl mx-auto space-y-4">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-500/10 border border-brand-500/20 text-xs font-medium text-brand-400">
          <Briefcase className="w-3.5 h-3.5" />
          <span>HomiQ Career & Contractor Network</span>
        </div>
        <h1 className="text-4xl font-bold text-white tracking-tight">
          Trade Specialist & Contractor Openings
        </h1>
        <p className="text-sm text-slate-400 max-w-xl mx-auto leading-relaxed">
          Join top enterprise facilities and maintenance teams. Work with flexible schedules, verified jobs, and weekly assured payouts.
        </p>

        {/* Search */}
        <div className="max-w-md mx-auto pt-2">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search by trade, role, or city..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-dark-850 border border-dark-700/80 rounded-xl pl-10 pr-4 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-brand-500 transition-colors"
            />
          </div>
        </div>
      </div>

      {/* Jobs Grid */}
      {isLoading ? (
        <LoadingState message="Loading active trade job openings..." />
      ) : filteredJobs.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredJobs.map((job) => (
            <Card key={job.id} className="flex flex-col justify-between space-y-4 group hover:border-dark-750">
              <div className="space-y-3">
                <div className="flex items-start justify-between">
                  <span className="text-[11px] font-mono text-slate-500">
                    Posted {new Date(job.created_at).toLocaleDateString()}
                  </span>
                  <span className="px-2 py-0.5 rounded text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold">
                    OPEN
                  </span>
                </div>

                <div>
                  <h3 className="text-base font-bold text-white group-hover:text-brand-400 transition-colors">
                    {job.title}
                  </h3>
                  <p className="text-xs text-brand-400 mt-0.5">
                    {job.company?.company_name || 'HomiQ Certified Enterprise Partner'}
                  </p>
                </div>

                <p className="text-xs text-slate-400 line-clamp-3 leading-relaxed">
                  {job.description}
                </p>

                <div className="flex flex-wrap items-center gap-3 text-xs text-slate-300 pt-1">
                  {job.location && (
                    <div className="flex items-center gap-1">
                      <MapPin className="w-3.5 h-3.5 text-brand-400" />
                      <span>{job.location}</span>
                    </div>
                  )}
                  {job.salary_range && (
                    <div className="flex items-center gap-1 font-mono text-emerald-400">
                      <DollarSign className="w-3.5 h-3.5" />
                      <span>{job.salary_range}</span>
                    </div>
                  )}
                </div>
              </div>

              <div className="pt-4 border-t border-dark-800/80 flex items-center justify-between">
                <span className="text-[11px] text-slate-500">Fast Review</span>
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => setSelectedJob(job)}
                  rightIcon={ArrowRight}
                >
                  Apply Now
                </Button>
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <EmptyState
          icon={Briefcase}
          title="No open positions match your search"
          description="Try different keywords or check back soon as new contractor listings are added daily."
        />
      )}

      {/* Application Modal */}
      {selectedJob && (
        <Modal
          isOpen={!!selectedJob}
          onClose={() => setSelectedJob(null)}
          title={`Apply for ${selectedJob.title}`}
          description={`Submit your candidacy to ${selectedJob.company?.company_name || 'Enterprise Team'}`}
          maxWidth="md"
        >
          <form onSubmit={handleApply} className="space-y-4">
            <div className="p-3.5 bg-dark-850 border border-dark-750 rounded-xl space-y-1 text-xs">
              <p className="font-bold text-white">Position: {selectedJob.title}</p>
              {selectedJob.location && <p className="text-slate-400">Location: {selectedJob.location}</p>}
              {selectedJob.salary_range && <p className="text-emerald-400">Compensation: {selectedJob.salary_range}</p>}
            </div>

            <Textarea
              label="Cover Note / Relevant Experience"
              placeholder="Highlight your trade certifications, years in the field, and availability..."
              rows={4}
              value={coverLetter}
              onChange={(e) => setCoverLetter(e.target.value)}
            />

            <div className="flex justify-end gap-3 pt-3 border-t border-dark-750">
              <Button variant="outline" size="sm" type="button" onClick={() => setSelectedJob(null)} disabled={isSubmitting}>
                Cancel
              </Button>
              <Button variant="primary" size="sm" type="submit" isLoading={isSubmitting} leftIcon={CheckCircle2}>
                Submit Application
              </Button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
};
