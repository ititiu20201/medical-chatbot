import React from 'react';
import { Card } from '@/components/ui/card';

const Layout = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <header className="mb-8">
          <h1 className="text-2xl font-bold text-center">
            Hệ thống Tư vấn Y tế
          </h1>
        </header>
        <main>
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;