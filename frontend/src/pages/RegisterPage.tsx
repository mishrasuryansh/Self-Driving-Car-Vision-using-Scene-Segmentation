import React from 'react';
import { UserPlus } from 'lucide-react';

export const RegisterPage: React.FC = () => (
  <div className="max-w-md mx-auto space-y-6 pt-10">
    <div className="text-center space-y-2">
      <UserPlus className="w-12 h-12 mx-auto text-cyan-400" />
      <h1 className="text-2xl font-bold">Create Account</h1>
      <p className="text-slate-400 text-sm">Register to process autonomous vehicle vision streams</p>
    </div>
    <form className="glass-card p-6 space-y-4">
      <div>
        <label className="block text-sm font-medium text-slate-300 mb-1">Full Name</label>
        <input type="text" required placeholder="Autonomous Driver" className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-slate-100" />
      </div>
      <div>
        <label className="block text-sm font-medium text-slate-300 mb-1">Email</label>
        <input type="email" required placeholder="driver@selfdriving.com" className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-slate-100" />
      </div>
      <div>
        <label className="block text-sm font-medium text-slate-300 mb-1">Password</label>
        <input type="password" required className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-slate-100" />
      </div>
      <button type="submit" className="w-full btn-primary mt-2">Register Account</button>
    </form>
  </div>
);
