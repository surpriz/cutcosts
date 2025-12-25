import type { Metadata } from "next";
import { Scale, Building, Server, User, Mail, Globe } from "lucide-react";

export const metadata: Metadata = {
  title: "Legal Notice - CutCosts | Mentions Légales",
  description:
    "CutCosts Legal Notice - Information about the publisher, hosting, and legal compliance.",
};

export default function LegalNoticePage() {
  return (
    <div className="prose prose-gray max-w-none">
      {/* Header */}
      <div className="not-prose mb-8">
        <div className="flex items-center gap-3 mb-4">
          <Scale className="w-8 h-8 text-blue-600" />
          <h1 className="text-4xl font-bold text-gray-900">Legal Notice</h1>
          <span className="text-sm text-gray-500">(Mentions Légales)</span>
        </div>
        <p className="text-gray-600 text-lg">
          Last updated: <strong>January 2025</strong>
        </p>
        <p className="text-gray-600 mt-2">
          This page provides legal information about CutCosts in compliance with French law (Article 6-III and
          19 of Law n° 2004-575 dated June 21, 2004 for Confidence in the Digital Economy - LCEN) and EU
          regulations.
        </p>
      </div>

      {/* 1. Publisher Information */}
      <section className="mb-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          <Building className="w-6 h-6 text-blue-600" />
          1. Publisher Information (Éditeur du Site)
        </h2>
        <div className="not-prose bg-blue-50 border border-blue-200 rounded-lg p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <p className="text-sm text-gray-600 mb-1">Company Name</p>
              <p className="font-semibold text-gray-900">JAAP v2 SASU</p>
            </div>
            <div>
              <p className="text-sm text-gray-600 mb-1">Trade Name</p>
              <p className="font-semibold text-gray-900">CutCosts</p>
            </div>
            <div>
              <p className="text-sm text-gray-600 mb-1">Legal Form</p>
              <p className="font-semibold text-gray-900">SASU (Société par Actions Simplifiée Unipersonnelle)</p>
            </div>
            <div>
              <p className="text-sm text-gray-600 mb-1">RCS Registration</p>
              <p className="font-semibold text-gray-900 font-mono">945 292 795 R.C.S. Romans</p>
            </div>
          </div>

          <div className="mt-6 pt-6 border-t border-blue-200">
            <p className="text-sm text-gray-600 mb-1">Registered Address</p>
            <p className="font-semibold text-gray-900">155 Chemin des Ecureuils</p>
            <p className="font-semibold text-gray-900">26450 Charols</p>
            <p className="font-semibold text-gray-900">France</p>
          </div>

          <div className="mt-6 pt-6 border-t border-blue-200">
            <p className="text-sm text-gray-600 mb-1">Contact</p>
            <p className="text-gray-900 flex items-center gap-2 mt-2">
              <Mail className="w-4 h-4 text-blue-600" />
              <a href="mailto:contact@cutcosts.tech" className="text-blue-600 hover:underline font-semibold">
                contact@cutcosts.tech
              </a>
            </p>
            <p className="text-gray-900 flex items-center gap-2 mt-2">
              <Globe className="w-4 h-4 text-blue-600" />
              <a href="https://cutcosts.tech" className="text-blue-600 hover:underline font-semibold">
                https://cutcosts.tech
              </a>
            </p>
          </div>
        </div>
      </section>

      {/* 2. Publication Director */}
      <section className="mb-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          <User className="w-6 h-6 text-blue-600" />
          2. Publication Director (Directeur de la Publication)
        </h2>
        <div className="not-prose bg-gray-50 border border-gray-200 rounded-lg p-6">
          <p className="text-gray-900">
            <strong>Name:</strong> Jérôme LAVAL
          </p>
          <p className="text-gray-900 mt-2">
            <strong>Position:</strong> President (Président)
          </p>
          <p className="text-gray-600 text-sm mt-4">
            The Publication Director is responsible for the content published on cutcosts.tech in accordance with
            French law (Article 93-2 of Law n° 82-652 of July 29, 1982).
          </p>
        </div>
      </section>

      {/* 3. Hosting Information */}
      <section className="mb-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          <Server className="w-6 h-6 text-blue-600" />
          3. Hosting Information (Hébergeur)
        </h2>
        <div className="not-prose bg-gray-50 border border-gray-200 rounded-lg p-6">
          <p className="text-gray-900">
            <strong>Host Name:</strong> Database Mart LLC
          </p>
          <p className="text-gray-900 mt-2">
            <strong>Address:</strong>
          </p>
          <p className="text-gray-700 ml-4">257 Westwood Dr</p>
          <p className="text-gray-700 ml-4">League City, TX 77573</p>
          <p className="text-gray-700 ml-4">United States</p>
          <p className="text-gray-900 mt-4">
            <strong>Contact:</strong>{" "}
            <a href="https://www.yourserver.se" className="text-blue-600 hover:underline">
              https://www.yourserver.se
            </a>
          </p>
        </div>

        <div className="not-prose bg-blue-50 border border-blue-200 rounded-lg p-4 mt-4">
          <p className="text-blue-900 text-sm">
            <strong>Server Location:</strong> The CutCosts application is hosted on servers located in{" "}
            <strong>the United States</strong>. Data transfers are conducted in compliance with GDPR requirements.
          </p>
        </div>
      </section>

      {/* 4. Intellectual Property */}
      <section className="mb-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">4. Intellectual Property</h2>
        <p>
          All content on cutcosts.tech (text, graphics, logos, icons, images, audio clips, digital downloads, data
          compilations, and software) is the property of CutCosts or its content suppliers and is protected by
          international copyright laws.
        </p>
        <p className="mt-4">
          The compilation of all content on this site is the exclusive property of CutCosts and is protected by
          international copyright laws. All software used on this site is the property of CutCosts or its software
          suppliers and is protected by international copyright laws.
        </p>

        <h3 className="text-xl font-semibold text-gray-900 mt-6 mb-3">Trademarks</h3>
        <p>
          "CutCosts" and the CutCosts logo are trademarks of CutCosts. All other trademarks, service marks,
          and trade names referenced on this site are the property of their respective owners.
        </p>

        <h3 className="text-xl font-semibold text-gray-900 mt-6 mb-3">Reproduction</h3>
        <p>
          Any reproduction, representation, modification, publication, or adaptation of all or part of the elements
          of the site, regardless of the means or process used, is prohibited without the prior written permission
          of CutCosts.
        </p>
      </section>

      {/* 5. Data Protection Officer (DPO) */}
      <section className="mb-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">5. Data Protection Officer (DPO)</h2>
        <p>
          In accordance with the General Data Protection Regulation (GDPR - Regulation EU 2016/679), CutCosts has
          appointed a Data Protection Officer (Délégué à la Protection des Données - DPD).
        </p>
        <div className="not-prose bg-gray-50 border border-gray-200 rounded-lg p-6 mt-4">
          <p className="text-gray-900">
            <strong>DPO Contact:</strong>
          </p>
          <p className="text-gray-900 mt-2 flex items-center gap-2">
            <Mail className="w-4 h-4 text-blue-600" />
            <a href="mailto:dpo@cutcosts.tech" className="text-blue-600 hover:underline font-semibold">
              dpo@cutcosts.tech
            </a>
          </p>
          <p className="text-gray-600 text-sm mt-4">
            For any questions about the processing of your personal data, please contact our DPO at the above
            address.
          </p>
        </div>
      </section>

      {/* 6. Applicable Law & Jurisdiction */}
      <section className="mb-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">6. Applicable Law and Jurisdiction</h2>
        <p>
          This website and its content are governed by <strong>French law</strong>.
        </p>
        <p className="mt-4">
          In the event of a dispute, and after an amicable resolution has failed, the courts of{" "}
          <strong>Valence (Drôme, France)</strong> shall have exclusive jurisdiction.
        </p>
        <div className="not-prose bg-yellow-50 border border-yellow-200 rounded-lg p-4 mt-4">
          <p className="text-yellow-900 text-sm">
            <strong>EU Consumers:</strong> If you are a consumer residing in the European Union, nothing in these
            provisions affects your mandatory consumer rights under EU law, including your right to bring legal
            action in your country of residence.
          </p>
        </div>
      </section>

      {/* 7. Cookies */}
      <section className="mb-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">7. Cookies</h2>
        <p>
          CutCosts uses cookies in accordance with applicable regulations, including the GDPR and the French Data
          Protection Act (Loi Informatique et Libertés).
        </p>
        <p className="mt-4">
          For detailed information about the cookies we use and how to manage them, please refer to our{" "}
          <a href="/legal/cookies" className="text-blue-600 hover:underline font-semibold">
            Cookie Policy
          </a>
          .
        </p>
      </section>

      {/* 8. Personal Data */}
      <section className="mb-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">8. Personal Data</h2>
        <p>
          CutCosts processes personal data in accordance with the GDPR and French data protection laws.
        </p>
        <p className="mt-4">
          For detailed information about how we collect, use, and protect your personal data, please refer to our{" "}
          <a href="/legal/privacy" className="text-blue-600 hover:underline font-semibold">
            Privacy Policy
          </a>
          .
        </p>

        <h3 className="text-xl font-semibold text-gray-900 mt-6 mb-3">Your Rights</h3>
        <p>
          Under the GDPR, you have the following rights:
        </p>
        <ul className="space-y-2 mt-2">
          <li>Right to access your personal data</li>
          <li>Right to rectification (correction of inaccurate data)</li>
          <li>Right to erasure ("right to be forgotten")</li>
          <li>Right to data portability</li>
          <li>Right to object to processing</li>
          <li>Right to restriction of processing</li>
          <li>Right to withdraw consent</li>
        </ul>
        <p className="mt-4">
          To exercise these rights, contact us at:{" "}
          <a href="mailto:privacy@cutcosts.tech" className="text-blue-600 hover:underline font-semibold">
            privacy@cutcosts.tech
          </a>
        </p>
      </section>

      {/* 9. Liability */}
      <section className="mb-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">9. Liability</h2>
        <p>
          CutCosts strives to provide accurate and up-to-date information on this website. However, we cannot
          guarantee the accuracy, completeness, or timeliness of the information provided.
        </p>
        <p className="mt-4">
          CutCosts shall not be held liable for:
        </p>
        <ul className="space-y-2 mt-2">
          <li>Errors or omissions in the content</li>
          <li>Technical issues or downtime</li>
          <li>Damages resulting from the use or inability to use the website</li>
          <li>Actions taken based on recommendations provided by the platform</li>
        </ul>
        <p className="mt-4 text-sm text-gray-600">
          For detailed information about liability limitations, please refer to our{" "}
          <a href="/legal/terms" className="text-blue-600 hover:underline">
            Terms of Service
          </a>
          .
        </p>
      </section>

      {/* 10. External Links */}
      <section className="mb-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">10. External Links (Liens Hypertextes)</h2>
        <p>
          CutCosts may contain links to external websites. We are not responsible for the content, privacy
          policies, or practices of these third-party websites.
        </p>
        <p className="mt-4">
          The inclusion of any link does not imply endorsement by CutCosts. We encourage you to review the terms
          and privacy policies of any external websites you visit.
        </p>
      </section>

      {/* 11. Reporting Illegal Content */}
      <section className="mb-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">11. Reporting Illegal Content (Signalement)</h2>
        <p>
          In accordance with Article 6.I.5 of the LCEN, if you believe that content on cutcosts.tech is illegal or
          violates your rights, you may report it by contacting:
        </p>
        <div className="not-prose bg-gray-50 border border-gray-200 rounded-lg p-6 mt-4">
          <p className="text-gray-900 flex items-center gap-2">
            <Mail className="w-4 h-4 text-blue-600" />
            <a href="mailto:legal@cutcosts.tech" className="text-blue-600 hover:underline font-semibold">
              legal@cutcosts.tech
            </a>
          </p>
          <p className="text-gray-600 text-sm mt-4">
            Please include:
          </p>
          <ul className="list-disc ml-6 text-gray-600 text-sm space-y-1 mt-2">
            <li>Your contact information</li>
            <li>A description of the allegedly illegal content</li>
            <li>The URL where the content is located</li>
            <li>The reason why you believe the content is illegal</li>
          </ul>
        </div>
      </section>

      {/* 12. Contact Information */}
      <section className="mb-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">12. Contact Information</h2>
        <p>
          For any questions about this Legal Notice or CutCosts, please contact us:
        </p>
        <div className="not-prose bg-blue-50 rounded-lg p-6 mt-4">
          <p className="text-gray-900 font-semibold text-lg">CutCosts</p>
          <p className="text-gray-700 mt-2">
            Email:{" "}
            <a href="mailto:contact@cutcosts.tech" className="text-blue-600 hover:underline font-semibold">
              contact@cutcosts.tech
            </a>
          </p>
          <p className="text-gray-700 mt-1">
            Legal:{" "}
            <a href="mailto:legal@cutcosts.tech" className="text-blue-600 hover:underline font-semibold">
              legal@cutcosts.tech
            </a>
          </p>
          <p className="text-gray-700 mt-1">
            Privacy:{" "}
            <a href="mailto:privacy@cutcosts.tech" className="text-blue-600 hover:underline font-semibold">
              privacy@cutcosts.tech
            </a>
          </p>
          <p className="text-gray-700 mt-4">
            Address: <span className="font-mono">155 Chemin des Ecureuils, 26450 Charols, France</span>
          </p>
        </div>
      </section>

      {/* Footer */}
      <div className="not-prose border-t border-gray-200 pt-8 mt-12">
        <p className="text-sm text-gray-500 text-center">
          © {new Date().getFullYear()} CutCosts. All rights reserved.
        </p>
        <p className="text-xs text-gray-400 text-center mt-2">
          This Legal Notice is compliant with French law (LCEN) and GDPR requirements.
        </p>
      </div>
    </div>
  );
}
