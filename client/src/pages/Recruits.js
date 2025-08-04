import React from 'react';
import { Users } from 'lucide-react';

const Recruits = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Potential Recruits</h1>
        <p className="mt-1 text-sm text-gray-500">
          Track and manage potential recruits from high schools and colleges
        </p>
      </div>

      <div className="card">
        <div className="card-body">
          <div className="text-center py-12">
            <Users className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">Potential Recruits</h3>
            <p className="mt-1 text-sm text-gray-500">
              This section will allow you to track potential recruits with their information including name, major, school, graduation years, and more.
            </p>
            <div className="mt-6">
              <div className="text-sm text-gray-500">
                <p>Features coming soon:</p>
                <ul className="mt-2 space-y-1">
                  <li>• Add new potential recruits</li>
                  <li>• Track recruitment status</li>
                  <li>• Generate reports</li>
                  <li>• Filter and search</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Recruits; 