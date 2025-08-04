import React from 'react';
import { UserCheck } from 'lucide-react';

const Cadre = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Cadre Management</h1>
        <p className="mt-1 text-sm text-gray-500">
          Manage existing AFROTC cadre members and their information
        </p>
      </div>

      <div className="card">
        <div className="card-body">
          <div className="text-center py-12">
            <UserCheck className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">Cadre Management</h3>
            <p className="mt-1 text-sm text-gray-500">
              This section will allow you to manage existing cadre members with their graduation year, major, cadet rank, hometown, officer interest, and enrollment status.
            </p>
            <div className="mt-6">
              <div className="text-sm text-gray-500">
                <p>Features coming soon:</p>
                <ul className="mt-2 space-y-1">
                  <li>• Add new cadre members</li>
                  <li>• Track enrollment status</li>
                  <li>• Record unenrollment reasons</li>
                  <li>• Generate cadre reports</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Cadre; 