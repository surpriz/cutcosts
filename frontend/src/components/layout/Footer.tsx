"use client";

import Link from "next/link";
import { Shield, FileText, Cookie, Scale, Mail, Github, Twitter, Linkedin } from "lucide-react";

export function Footer() {
  const handleOpenCookieSettings = () => {
    if (typeof window !== "undefined" && (window as any).openCookieSettings) {
      (window as any).openCookieSettings();
    }
  };

  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-zinc-950 text-zinc-400 border-t border-zinc-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {/* Company Info */}
          <div className="space-y-4">
            <h3 className="text-2xl font-bold">
              <span className="text-zinc-50">Cut</span>
              <span className="gradient-text-cyan-violet">Costs</span>
            </h3>
            <p className="text-sm text-zinc-500">
              Detect orphaned cloud resources and reduce your cloud costs automatically.
            </p>
            <div className="flex gap-3">
              <a
                href="https://github.com/cloudwaste"
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 hover:bg-zinc-900 rounded-lg transition-colors text-zinc-500 hover:text-zinc-300"
                aria-label="GitHub"
              >
                <Github className="w-5 h-5" />
              </a>
              <a
                href="https://twitter.com/cloudwaste"
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 hover:bg-zinc-900 rounded-lg transition-colors text-zinc-500 hover:text-zinc-300"
                aria-label="Twitter"
              >
                <Twitter className="w-5 h-5" />
              </a>
              <a
                href="https://linkedin.com/company/cloudwaste"
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 hover:bg-zinc-900 rounded-lg transition-colors text-zinc-500 hover:text-zinc-300"
                aria-label="LinkedIn"
              >
                <Linkedin className="w-5 h-5" />
              </a>
            </div>
          </div>

          {/* Product Links */}
          <div>
            <h4 className="text-zinc-50 font-semibold mb-4">Product</h4>
            <ul className="space-y-3 text-sm">
              <li>
                <Link href="/dashboard" className="text-zinc-500 hover:text-zinc-300 transition-colors">
                  Dashboard
                </Link>
              </li>
              <li>
                <Link href="/dashboard/accounts" className="text-zinc-500 hover:text-zinc-300 transition-colors">
                  Cloud Accounts
                </Link>
              </li>
              <li>
                <Link href="/dashboard/scans" className="text-zinc-500 hover:text-zinc-300 transition-colors">
                  Scans
                </Link>
              </li>
              <li>
                <Link href="/dashboard/resources" className="text-zinc-500 hover:text-zinc-300 transition-colors">
                  Resources
                </Link>
              </li>
              <li>
                <Link href="/api/docs" target="_blank" rel="noopener noreferrer" className="text-zinc-500 hover:text-zinc-300 transition-colors">
                  API Documentation
                </Link>
              </li>
            </ul>
          </div>

          {/* Legal Links */}
          <div>
            <h4 className="text-zinc-50 font-semibold mb-4">Legal</h4>
            <ul className="space-y-3 text-sm">
              <li>
                <Link
                  href="/legal/privacy"
                  className="text-zinc-500 hover:text-zinc-300 transition-colors flex items-center gap-2"
                >
                  <Shield className="w-4 h-4" />
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link
                  href="/legal/terms"
                  className="text-zinc-500 hover:text-zinc-300 transition-colors flex items-center gap-2"
                >
                  <FileText className="w-4 h-4" />
                  Terms of Service
                </Link>
              </li>
              <li>
                <Link
                  href="/legal/cookies"
                  className="text-zinc-500 hover:text-zinc-300 transition-colors flex items-center gap-2"
                >
                  <Cookie className="w-4 h-4" />
                  Cookie Policy
                </Link>
              </li>
              <li>
                <Link
                  href="/legal/legal-notice"
                  className="text-zinc-500 hover:text-zinc-300 transition-colors flex items-center gap-2"
                >
                  <Scale className="w-4 h-4" />
                  Legal Notice
                </Link>
              </li>
              <li>
                <button
                  onClick={handleOpenCookieSettings}
                  className="text-zinc-500 hover:text-zinc-300 transition-colors flex items-center gap-2 text-left"
                >
                  <Cookie className="w-4 h-4" />
                  Cookie Settings
                </button>
              </li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h4 className="text-zinc-50 font-semibold mb-4">Contact</h4>
            <ul className="space-y-3 text-sm">
              <li>
                <a
                  href="mailto:support@cloudwaste.com"
                  className="text-zinc-500 hover:text-zinc-300 transition-colors flex items-center gap-2"
                >
                  <Mail className="w-4 h-4" />
                  Support
                </a>
              </li>
              <li>
                <a
                  href="mailto:contact@cloudwaste.com"
                  className="text-zinc-500 hover:text-zinc-300 transition-colors flex items-center gap-2"
                >
                  <Mail className="w-4 h-4" />
                  General Inquiries
                </a>
              </li>
              <li>
                <a
                  href="mailto:privacy@cloudwaste.com"
                  className="text-zinc-500 hover:text-zinc-300 transition-colors flex items-center gap-2"
                >
                  <Mail className="w-4 h-4" />
                  Privacy
                </a>
              </li>
              <li>
                <a
                  href="mailto:legal@cloudwaste.com"
                  className="text-zinc-500 hover:text-zinc-300 transition-colors flex items-center gap-2"
                >
                  <Mail className="w-4 h-4" />
                  Legal
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="mt-12 pt-8 border-t border-zinc-900">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-sm text-zinc-500">
              © {currentYear} CutCosts. All rights reserved.
            </p>
            <div className="flex flex-wrap justify-center gap-4 text-xs text-zinc-500">
              <span className="flex items-center gap-1">
                <span className="text-emerald-400">●</span> GDPR Compliant
              </span>
              <span className="text-zinc-700">•</span>
              <span className="flex items-center gap-1">
                <span className="text-cyan-400">●</span> ISO 27001
              </span>
              <span className="text-zinc-700">•</span>
              <span className="flex items-center gap-1">
                <span className="text-violet-400">●</span> SOC 2 Type II
              </span>
            </div>
          </div>

          <p className="text-xs text-zinc-600 text-center mt-4">
            Built with FastAPI & Next.js | Hosted in the EU
          </p>
        </div>
      </div>
    </footer>
  );
}
