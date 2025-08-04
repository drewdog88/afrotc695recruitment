import React from 'react';
import { Phone } from 'lucide-react';

const Contacts = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">University Contacts</h1>
        <p className="mt-1 text-sm text-gray-500">
          Manage contacts at various universities for recruitment coordination
        </p>
      </div>

      <div className="card">
        <div className="card-body">
          <div className="text-center py-12">
            <Phone className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">University Contacts</h3>
            <p className="mt-1 text-sm text-gray-500">
              This section will allow you to maintain a list of contacts at various universities for coordinating recruitment days and events.
            </p>
            <div className="mt-6">
              <div className="text-sm text-gray-500">
                <p>Features coming soon:</p>
                <ul className="mt-2 space-y-1">
                  <li>• Add university contacts</li>
                  <li>• Store contact information</li>
                  <li>• Track active/inactive contacts</li>
                  <li>• Link contacts to events</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Contacts; 