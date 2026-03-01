import Link from 'next/link'
import { Briefcase, Brain, Zap, Mail } from 'lucide-react'

export default function Home() {
  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <section className="text-center py-12">
        <h1 className="text-4xl font-bold text-gray-900 sm:text-5xl md:text-6xl">
          <span className="block">Jarvis Job Hunter</span>
          <span className="block text-primary-600 text-2xl sm:text-3xl mt-2">
            Your AI-Powered Job Search Assistant
          </span>
        </h1>
        <p className="mt-6 max-w-2xl mx-auto text-xl text-gray-500">
          Automated job sourcing for frontier tech roles in Spain.
          Identifies HQP Visa eligible companies and enables 1-click applications.
        </p>
        <div className="mt-8 flex justify-center gap-4">
          <Link
            href="/dashboard"
            className="px-8 py-3 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition"
          >
            View Jobs
          </Link>
          <Link
            href="/profile"
            className="px-8 py-3 bg-white text-primary-600 border border-primary-600 rounded-lg font-medium hover:bg-primary-50 transition"
          >
            Upload Resume
          </Link>
        </div>
      </section>

      {/* Features Grid */}
      <section className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
        <FeatureCard
          icon={<Briefcase className="w-8 h-8" />}
          title="Hunter Engine"
          description="Automatically polls TheirStack and Google Jobs for new opportunities every 15 minutes."
        />
        <FeatureCard
          icon={<Brain className="w-8 h-8" />}
          title="AI Analysis"
          description="Gemini-powered fit scoring, skill matching, and visa eligibility detection."
        />
        <FeatureCard
          icon={<Zap className="w-8 h-8" />}
          title="Auto Apply"
          description="One-click applications with intelligent form filling using your profile."
        />
        <FeatureCard
          icon={<Mail className="w-8 h-8" />}
          title="Cold Outreach"
          description="AI-generated personalized emails with verified contact discovery."
        />
      </section>

      {/* Quick Stats */}
      <section className="bg-white rounded-xl shadow-sm p-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">Quick Stats</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <StatCard label="Total Jobs" value="--" />
          <StatCard label="High Fit (70+)" value="--" />
          <StatCard label="HQP Eligible" value="--" />
          <StatCard label="Applied" value="--" />
        </div>
        <p className="mt-4 text-sm text-gray-500 text-center">
          Upload your resume to start tracking personalized stats
        </p>
      </section>
    </div>
  )
}

function FeatureCard({
  icon,
  title,
  description
}: {
  icon: React.ReactNode
  title: string
  description: string
}) {
  return (
    <div className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition">
      <div className="text-primary-600 mb-4">{icon}</div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-600 text-sm">{description}</p>
    </div>
  )
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="text-center">
      <div className="text-3xl font-bold text-primary-600">{value}</div>
      <div className="text-sm text-gray-500 mt-1">{label}</div>
    </div>
  )
}
