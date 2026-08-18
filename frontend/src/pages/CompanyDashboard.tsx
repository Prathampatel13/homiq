import React, { useState, useEffect, useCallback } from 'react';
import {
  Building2,
  Briefcase,
  Users,
  Plus,
  Trash2,
  Edit2,
  CheckCircle2,
  XCircle,
  ExternalLink,
  ChevronRight,
} from 'lucide-react';
import { companyApi } from '../api/company';
import { jobsApi } from '../api/jobs';
import { CompanyProfile, JobApplication, JobPost } from '../types';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { StatsCard } from '../components/ui/StatsCard';
import { Tabs } from '../components/ui/Tabs';
import { Input } from '../components/ui/Input';
import { Textarea } from '../components/ui/Textarea';
import { Modal } from '../components/ui/Modal';
import { LoadingState } from '../components/ui/LoadingState';
import { EmptyState } from '../components/ui/EmptyState';
import { useToast } from '../components/ui/Toast';
import { extractErrorMessage } from '../api/axios';
import { useAuthStore } from '../store/useAuthStore';

export const CompanyDashboard: React.FC = () => {
  const toast = useToast();
  const { user } = useAuthStore();

  const [activeTab, setActiveTab] = useState('jobs');
  const [profile, setProfile] = useState<CompanyProfile | null>(null);
  const [myJobs, setMyJobs] = useState<JobPost[]>([]);
  const [applications, setApplications] = useState<JobApplication[]>([]);
  const [selectedJobForApps, setSelectedJobForApps] = useState<JobPost | null>(null);

  const [isLoading, setIsLoading] = useState(true);

  // Job creation modal
  const [isJobModalOpen, setIsJobModalOpen] = useState(false);
  const [jobForm, setJobForm] = useState({
    title: '',
    description: '',
    requirements: '',
    location: '',
    salary_range: '',
  });
  const [isSubmittingJob, setIsSubmittingJob] = useState(false);

  // Company Profile form
  const [profileForm, setProfileForm] = useState({
    company_name: '',
    industry: '',
    description: '',
    website: '',
  });
  const [isSavingProfile, setIsSavingProfile] = useState(false);

  const fetchCompanyData = useCallback(async () => {
    try {
      const [profData, jobsData] = await Promise.all([
        companyApi.getProfile().catch(() => null),
        jobsApi.getMyJobs().catch(() => []),
      ]);

      if (profData) {
        setProfile(profData);
        setProfileForm({
          company_name: profData.company_name || '',
          industry: profData.industry || '',
          description: profData.description || '',
          website: profData.website || '',
        });
      }

      setMyJobs(jobsData);
    } catch (err) {
      toast.error('Could not load company portal', extractErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }, [toast]);

  useEffect(() => {
    fetchCompanyData();
  }, [fetchCompanyData]);

  const handleCreateJob = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!jobForm.title.trim() || !jobForm.description.trim()) {
      toast.error('Required Fields', 'Please provide job title and description.');
      return;
    }

    setIsSubmittingJob(true);
    try {
      await jobsApi.createJob(jobForm);
      toast.success('Job Opening Created', 'Published to trade recruitment portal.');
      setIsJobModalOpen(false);
      setJobForm({ title: '', description: '', requirements: '', location: '', salary_range: '' });
      fetchCompanyData();
    } catch (err) {
      toast.error('Failed to create job', extractErrorMessage(err));
    } finally {
      setIsSubmittingJob(false);
    }
  };

  const handleViewApplicants = async (job: JobPost) => {
    setSelectedJobForApps(job);
    try {
      const apps = await jobsApi.getJobApplications(job.id);
      setApplications(apps);
      setActiveTab('applicants');
    } catch (err) {
      toast.error('Could not load applicants', extractErrorMessage(err));
    }
  };

  const handleUpdateApplicationStatus = async (appId: number, status: string) => {
    try {
      await jobsApi.updateApplicationStatus(appId, status);
      toast.success('Applicant Updated', `Status changed to ${status}.`);
      setApplications((prev) => prev.map((a) => (a.id === appId ? { ...a, status } : a)));
    } catch (err) {
      toast.error('Could not update status', extractErrorMessage(err));
    }
  };

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSavingProfile(true);
    try {
      const updated = await companyApi.updateProfile(profileForm);
      setProfile(updated);
      toast.success('Company Profile Updated');
    } catch (err) {
      toast.error('Failed to save profile', extractErrorMessage(err));
    } finally {
      setIsSavingProfile(false);
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-20">
        <LoadingState message="Loading company operations gateway..." />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-dark-750">
        <div>
          <p className="text-xs font-mono uppercase tracking-widest text-brand-400 font-semibold mb-1">
            Enterprise & Contractor Hub
          </p>
          <h1 className="text-3xl font-bold text-white tracking-tight">
            {profile?.company_name || 'Enterprise'} Command Center
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Recruit trade technicians, manage corporate job postings, and review candidates.
          </p>
        </div>

        <Button
          variant="primary"
          size="md"
          leftIcon={Plus}
          onClick={() => setIsJobModalOpen(true)}
        >
          Post New Opening
        </Button>
      </div>

      {/* KPI STATS */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <StatsCard
          label="Active Job Openings"
          value={myJobs.length}
          icon={Briefcase}
          subtext="Recruitment listings"
        />
        <StatsCard
          label="Total Applications"
          value={applications.length || '—'}
          icon={Users}
          subtext="Technician candidates"
        />
        <StatsCard
          label="Industry"
          value={profile?.industry || 'Trade Services'}
          icon={Building2}
          subtext="Verified Enterprise"
        />
      </div>

      {/* TABS */}
      <div className="space-y-6">
        <Tabs
          tabs={[
            { id: 'jobs', label: 'Job Openings', count: myJobs.length },
            { id: 'applicants', label: 'Applicant Pipeline', count: applications.length },
            { id: 'profile', label: 'Company Profile' },
          ]}
          activeTab={activeTab}
          onChange={setActiveTab}
          variant="underline"
        />

        {/* TAB 1: JOB OPENINGS */}
        {activeTab === 'jobs' && (
          <div className="space-y-4">
            {myJobs.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {myJobs.map((job) => (
                  <Card key={job.id} className="p-5 flex flex-col justify-between space-y-3">
                    <div>
                      <div className="flex justify-between items-start">
                        <span className="text-[11px] font-mono text-slate-500">
                          {new Date(job.created_at).toLocaleDateString()}
                        </span>
                        <span className="px-2 py-0.5 rounded text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold">
                          ACTIVE
                        </span>
                      </div>
                      <h4 className="text-base font-bold text-white mt-1">{job.title}</h4>
                      <p className="text-xs text-slate-400 mt-1 line-clamp-2">{job.description}</p>

                      <div className="flex items-center gap-4 text-xs text-slate-400 pt-2">
                        {job.location && <span>📍 {job.location}</span>}
                        {job.salary_range && <span>💰 {job.salary_range}</span>}
                      </div>
                    </div>

                    <div className="pt-3 border-t border-dark-800 flex justify-end">
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => handleViewApplicants(job)}
                        rightIcon={ChevronRight}
                      >
                        View Applicants
                      </Button>
                    </div>
                  </Card>
                ))}
              </div>
            ) : (
              <EmptyState
                icon={Briefcase}
                title="No job openings posted"
                description="Post your first trade job listing to attract verified technicians."
                actionLabel="Create Opening"
                onAction={() => setIsJobModalOpen(true)}
              />
            )}
          </div>
        )}

        {/* TAB 2: APPLICANTS PIPELINE */}
        {activeTab === 'applicants' && (
          <div className="space-y-4">
            {selectedJobForApps && (
              <div className="p-4 bg-dark-850 rounded-xl border border-dark-750 flex items-center justify-between">
                <div>
                  <span className="text-xs text-slate-400">Showing applicants for:</span>
                  <h4 className="text-sm font-bold text-white">{selectedJobForApps.title}</h4>
                </div>
                <button
                  onClick={() => setSelectedJobForApps(null)}
                  className="text-xs text-brand-400 hover:underline"
                >
                  Clear filter
                </button>
              </div>
            )}

            {applications.length > 0 ? (
              <div className="p-4 bg-dark-900 border border-dark-750 rounded-2xl divide-y divide-dark-800">
                {applications.map((app) => (
                  <div key={app.id} className="py-4 space-y-3">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                      <div>
                        <h5 className="text-sm font-bold text-white">
                          {(app.technician as any)?.user?.full_name || (app.technician as any)?.full_name || `Applicant #${app.technician_id}`}
                        </h5>
                        <p className="text-xs text-slate-400">
                          {(app.technician as any)?.specialization || 'Certified Field Specialist'} • Applied on{' '}
                          {new Date(app.created_at).toLocaleDateString()}
                        </p>
                      </div>

                      <span
                        className={`px-2.5 py-0.5 rounded-full text-xs font-semibold uppercase ${
                          app.status === 'hired'
                            ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                            : app.status === 'shortlisted'
                            ? 'bg-brand-500/15 text-brand-400 border border-brand-500/30'
                            : app.status === 'rejected'
                            ? 'bg-rose-500/15 text-rose-400 border border-rose-500/30'
                            : 'bg-dark-800 text-slate-300 border border-dark-700'
                        }`}
                      >
                        {app.status}
                      </span>
                    </div>

                    {app.cover_letter && (
                      <p className="text-xs text-slate-300 bg-dark-850 p-3 rounded-xl border border-dark-750">
                        "{app.cover_letter}"
                      </p>
                    )}

                    <div className="flex items-center gap-2 pt-1">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleUpdateApplicationStatus(app.id, 'shortlisted')}
                      >
                        Shortlist
                      </Button>
                      <Button
                        variant="primary"
                        size="sm"
                        onClick={() => handleUpdateApplicationStatus(app.id, 'hired')}
                        leftIcon={CheckCircle2}
                      >
                        Hire
                      </Button>
                      <Button
                        variant="danger"
                        size="sm"
                        onClick={() => handleUpdateApplicationStatus(app.id, 'rejected')}
                      >
                        Reject
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState
                icon={Users}
                title="No applicants yet"
                description="When trade technicians apply for your openings, they will appear here for review."
              />
            )}
          </div>
        )}

        {/* TAB 3: COMPANY PROFILE */}
        {activeTab === 'profile' && (
          <div className="max-w-2xl space-y-6">
            <h3 className="text-base font-bold text-white">Company Profile Details</h3>
            <form onSubmit={handleSaveProfile} className="space-y-4">
              <Input
                label="Company / Enterprise Legal Name"
                value={profileForm.company_name}
                onChange={(e) => setProfileForm({ ...profileForm, company_name: e.target.value })}
                required
              />
              <Input
                label="Industry / Domain"
                placeholder="e.g. Commercial HVAC, Facilities Management"
                value={profileForm.industry}
                onChange={(e) => setProfileForm({ ...profileForm, industry: e.target.value })}
              />
              <Input
                label="Official Website URL"
                placeholder="https://example.com"
                value={profileForm.website}
                onChange={(e) => setProfileForm({ ...profileForm, website: e.target.value })}
              />
              <Textarea
                label="Corporate Description"
                placeholder="Tell technicians about your enterprise..."
                rows={4}
                value={profileForm.description}
                onChange={(e) => setProfileForm({ ...profileForm, description: e.target.value })}
              />

              <div className="pt-3">
                <Button variant="primary" size="md" type="submit" isLoading={isSavingProfile}>
                  Save Enterprise Details
                </Button>
              </div>
            </form>
          </div>
        )}
      </div>

      {/* Job Creation Modal */}
      <Modal
        isOpen={isJobModalOpen}
        onClose={() => setIsJobModalOpen(false)}
        title="Post New Trade Job Opening"
        description="Listings will be instantly visible to qualified technicians on the HomiQ Recruitment board."
        maxWidth="lg"
      >
        <form onSubmit={handleCreateJob} className="space-y-4">
          <Input
            label="Job Title *"
            placeholder="e.g. Senior HVAC Diagnostic Technician"
            value={jobForm.title}
            onChange={(e) => setJobForm({ ...jobForm, title: e.target.value })}
            required
          />

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input
              label="Location / Region"
              placeholder="e.g. Bengaluru North"
              value={jobForm.location}
              onChange={(e) => setJobForm({ ...jobForm, location: e.target.value })}
            />
            <Input
              label="Compensation / Salary Range"
              placeholder="e.g. ₹35,000 - ₹50,000 / month"
              value={jobForm.salary_range}
              onChange={(e) => setJobForm({ ...jobForm, salary_range: e.target.value })}
            />
          </div>

          <Textarea
            label="Job Description *"
            placeholder="Describe day-to-day responsibilities, dispatch shifts, and tools provided..."
            rows={4}
            value={jobForm.description}
            onChange={(e) => setJobForm({ ...jobForm, description: e.target.value })}
            required
          />

          <Textarea
            label="Requirements & Qualifications"
            placeholder="e.g. 3+ years experience, ITI Certificate, Valid 2-wheeler license..."
            rows={3}
            value={jobForm.requirements}
            onChange={(e) => setJobForm({ ...jobForm, requirements: e.target.value })}
          />

          <div className="flex items-center justify-end gap-3 pt-3 border-t border-dark-750">
            <Button variant="outline" size="sm" type="button" onClick={() => setIsJobModalOpen(false)} disabled={isSubmittingJob}>
              Cancel
            </Button>
            <Button variant="primary" size="sm" type="submit" isLoading={isSubmittingJob}>
              Publish Opening
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
