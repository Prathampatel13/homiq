import React, { useEffect, useState } from 'react';
import { Plus, Users, Briefcase, Trash2, Edit } from 'lucide-react';
import api from '../../api/axios';
import { EmptyState } from '../ui/EmptyState';
import { LoadingState } from '../ui/LoadingState';
import { useAuthStore } from '../../store/useAuthStore';

interface JobPost {
  id: number;
  title: string;
  description: string;
  requirements: string;
  is_active: boolean;
  application_count: number;
  created_at: string;
}

export const ProviderRecruitmentTab: React.FC = () => {
  const [jobs, setJobs] = useState<JobPost[]>([]);
  const [loading, setLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    requirements: '',
    is_active: true
  });

  const fetchJobs = async () => {
    try {
      setLoading(true);
      const res = await api.get('/jobs/my');
      setJobs(res.data?.items || []);
    } catch (e) {
      console.error('Failed to fetch jobs', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/jobs/', formData);
      setIsCreating(false);
      setFormData({ title: '', description: '', requirements: '', is_active: true });
      fetchJobs();
    } catch (e) {
      console.error(e);
      alert('Failed to create job');
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this job opening?')) return;
    try {
      await api.delete(`/jobs/${id}`);
      fetchJobs();
    } catch (e) {
      console.error(e);
      alert('Failed to delete job');
    }
  };

  if (loading) return <LoadingState message="Loading Openings..." />;

  if (isCreating) {
    return (
      <div className="bg-dark-900 border border-dark-750 p-6 rounded-3xl shadow-card">
        <h3 className="text-xl font-bold mb-4">Create Job Opening</h3>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm text-slate-400 mb-1">Job Title</label>
            <input 
              required
              type="text" 
              className="w-full bg-dark-950 border border-dark-750 rounded-xl px-4 py-2 text-white focus:outline-none focus:border-sage-400"
              value={formData.title}
              onChange={e => setFormData({...formData, title: e.target.value})}
              placeholder="e.g. Apprentice Electrician"
            />
          </div>
          <div>
            <label className="block text-sm text-slate-400 mb-1">Description</label>
            <textarea 
              className="w-full bg-dark-950 border border-dark-750 rounded-xl px-4 py-2 text-white focus:outline-none focus:border-sage-400 h-24"
              value={formData.description}
              onChange={e => setFormData({...formData, description: e.target.value})}
              placeholder="Describe the role and responsibilities..."
            />
          </div>
          <div>
            <label className="block text-sm text-slate-400 mb-1">Requirements</label>
            <textarea 
              className="w-full bg-dark-950 border border-dark-750 rounded-xl px-4 py-2 text-white focus:outline-none focus:border-sage-400 h-24"
              value={formData.requirements}
              onChange={e => setFormData({...formData, requirements: e.target.value})}
              placeholder="List required skills and experience..."
            />
          </div>
          <div className="flex justify-end gap-3 pt-4">
            <button 
              type="button" 
              onClick={() => setIsCreating(false)}
              className="px-4 py-2 rounded-xl text-sm font-semibold bg-dark-800 text-slate-300 hover:bg-dark-750"
            >
              Cancel
            </button>
            <button 
              type="submit" 
              className="px-4 py-2 rounded-xl text-sm font-bold bg-sage-400 text-dark-950 hover:bg-sage-300"
            >
              Post Opening
            </button>
          </div>
        </form>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-xl font-bold tracking-tight">Staff Recruitment</h3>
          <p className="text-sm text-slate-400 mt-1">Manage your active job openings and applications.</p>
        </div>
        <button 
          onClick={() => setIsCreating(true)}
          className="btn-primary text-sm px-4 py-2 flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          <span>New Opening</span>
        </button>
      </div>

      {jobs.length === 0 ? (
        <EmptyState 
          title="No Active Openings" 
          description="Create a job opening to start hiring staff and technicians."
          icon={Briefcase}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {jobs.map(job => (
            <div key={job.id} className="p-5 rounded-2xl bg-dark-900 border border-dark-750 hover:border-dark-700 transition-colors shadow-card flex flex-col gap-4 relative">
              <div className="absolute top-4 right-4 flex items-center gap-2">
                <button onClick={() => handleDelete(job.id)} className="text-red-400 hover:text-red-300 p-1 bg-red-500/10 rounded-lg">
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
              <div>
                <h4 className="text-lg font-bold text-white pr-10">{job.title}</h4>
                <div className="flex flex-wrap items-center gap-2 mt-2">
                  <span className={`text-[10px] font-mono px-2 py-1 rounded border ${job.is_active ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' : 'bg-dark-800 text-slate-400 border-dark-750'}`}>
                    {job.is_active ? 'ACTIVE' : 'PAUSED'}
                  </span>
                  <span className="text-[10px] font-mono text-slate-400">
                    Posted: {new Date(job.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
              
              <div className="pt-4 border-t border-dark-800">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5 text-sage-400">
                    <Users className="w-4 h-4" />
                    <span className="font-bold text-sm">{job.application_count} Applicants</span>
                  </div>
                  {job.application_count > 0 && (
                    <button className="text-xs font-mono font-bold text-white bg-dark-850 px-3 py-1.5 rounded-lg border border-dark-750 hover:bg-dark-800 transition-colors">
                      VIEW
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
