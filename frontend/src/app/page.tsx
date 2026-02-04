import {
  LandingNav,
  HeroSection,
  StatsGrid,
  FeaturesSection,
  HowItWorks,
  CTASection,
} from "@/components/landing";
import { Footer } from "@/components/layout/Footer";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col bg-landing-deep">
      <LandingNav />
      <HeroSection />
      <StatsGrid />
      <FeaturesSection />
      <HowItWorks />
      <CTASection />
      <Footer />
    </main>
  );
}
