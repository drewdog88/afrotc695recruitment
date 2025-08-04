import React from 'react';
import { Settings } from 'lucide-react';

const Admin = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Administration</h1>
        <p className="mt-1 text-sm text-gray-500">
          System administration and user management
        </p>
      </div>

      <div className="card">
        <div className="card-body">
          <div className="text-center py-12">
            <Settings className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">Administration Panel</h3>
            <p className="mt-1 text-sm text-gray-500">
              This section will allow you to manage users, view system statistics, and access administrative functions.
            </p>
            <div className="mt-6">
              <div className="text-sm text-gray-500">
                <p>Features coming soon:</p>
                <ul className="mt-2 space-y-1">
                  <li>• User management</li>
                  <li>• System statistics</li>
                  <li>• Usage tracking</li>
                  <li>• Security settings</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Admin; 