'use client'

import { useState, useEffect } from 'react'
import { Upload, User, Linkedin } from 'lucide-react'
import { uploadResume, getProfile, enrichLinkedIn } from '@/lib/api'

type Profile = {
  id: string
  profile_json: {
    name?: string
    email?: string
    summary?: string
    skills?: string[]
    experience?: Array<{
      title: string
      company: string
      start_date?: string
      end_date?: string
    }>
    education?: Array<{
      degree: string
      institution: string
    }>
    languages?: string[]
  }
  resume_url?: string
  linkedin_url?: string
  updated_at: string
}

export default function ProfilePage() {
  const [profile, setProfile] = useState<Profile | null>(null)
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [linkedinUrl, setLinkedinUrl] = useState('')
  const [enriching, setEnriching] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  useEffect(() => {
    loadProfile()
  }, [])

  async function loadProfile() {
    try {
      const data = await getProfile()
      setProfile(data)
    } catch (err) {
      // Profile not found is expected for new users
      console.log('No profile found')
    } finally {
      setLoading(false)
    }
  }

  async function handleFileUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return

    setUploading(true)
    setMessage(null)

    try {
      await uploadResume(file)
      setMessage({ type: 'success', text: 'Resume uploaded and parsed successfully!' })
      loadProfile()
    } catch (err) {
      setMessage({ type: 'error', text: 'Failed to upload resume. Please try again.' })
    } finally {
      setUploading(false)
    }
  }

  async function handleLinkedInEnrich() {
    if (!linkedinUrl) return

    setEnriching(true)
    setMessage(null)

    try {
      await enrichLinkedIn(linkedinUrl)
      setMessage({ type: 'success', text: 'Profile enriched with LinkedIn data!' })
      loadProfile()
    } catch (err) {
      setMessage({ type: 'error', text: 'Failed to enrich profile. Please check the URL and try again.' })
    } finally {
      setEnriching(false)
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <h1 className="text-2xl font-bold text-gray-900">Your Profile</h1>

      {/* Message */}
      {message && (
        <div className={`px-4 py-3 rounded-lg ${
          message.type === 'success'
            ? 'bg-green-50 border border-green-200 text-green-700'
            : 'bg-red-50 border border-red-200 text-red-700'
        }`}>
          {message.text}
        </div>
      )}

      {/* Upload Section */}
      <section className="bg-white rounded-xl shadow-sm p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Upload className="w-5 h-5" />
          Upload Resume
        </h2>
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-primary-500 transition">
          <input
            type="file"
            accept=".pdf"
            onChange={handleFileUpload}
            disabled={uploading}
            className="hidden"
            id="resume-upload"
          />
          <label htmlFor="resume-upload" className="cursor-pointer">
            <Upload className="w-12 h-12 mx-auto text-gray-400 mb-4" />
            <p className="text-gray-600">
              {uploading ? 'Uploading...' : 'Click to upload your resume (PDF)'}
            </p>
            <p className="text-sm text-gray-400 mt-2">
              Your resume will be parsed and used for job matching
            </p>
          </label>
        </div>
        {profile?.resume_url && (
          <p className="mt-4 text-sm text-gray-500">
            Current resume: <a href={profile.resume_url} target="_blank" className="text-primary-600 hover:underline">View PDF</a>
          </p>
        )}
      </section>

      {/* LinkedIn Enrichment */}
      <section className="bg-white rounded-xl shadow-sm p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Linkedin className="w-5 h-5" />
          LinkedIn Enrichment
        </h2>
        <div className="flex gap-4">
          <input
            type="url"
            value={linkedinUrl}
            onChange={(e) => setLinkedinUrl(e.target.value)}
            placeholder="https://linkedin.com/in/your-profile"
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg"
          />
          <button
            onClick={handleLinkedInEnrich}
            disabled={enriching || !linkedinUrl}
            className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
          >
            {enriching ? 'Enriching...' : 'Enrich'}
          </button>
        </div>
        {profile?.linkedin_url && (
          <p className="mt-4 text-sm text-gray-500">
            Connected: <a href={profile.linkedin_url} target="_blank" className="text-primary-600 hover:underline">{profile.linkedin_url}</a>
          </p>
        )}
      </section>

      {/* Profile Display */}
      {profile && (
        <section className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <User className="w-5 h-5" />
            Parsed Profile
          </h2>

          <div className="space-y-6">
            {/* Basic Info */}
            <div>
              <h3 className="font-medium text-gray-900">{profile.profile_json.name || 'Name not found'}</h3>
              <p className="text-gray-500">{profile.profile_json.email}</p>
            </div>

            {/* Summary */}
            {profile.profile_json.summary && (
              <div>
                <h4 className="text-sm font-medium text-gray-500 mb-1">Summary</h4>
                <p className="text-gray-700">{profile.profile_json.summary}</p>
              </div>
            )}

            {/* Skills */}
            {profile.profile_json.skills && profile.profile_json.skills.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-gray-500 mb-2">Skills</h4>
                <div className="flex flex-wrap gap-2">
                  {profile.profile_json.skills.map((skill, i) => (
                    <span key={i} className="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm">
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Experience */}
            {profile.profile_json.experience && profile.profile_json.experience.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-gray-500 mb-2">Experience</h4>
                <div className="space-y-3">
                  {profile.profile_json.experience.slice(0, 3).map((exp, i) => (
                    <div key={i} className="border-l-2 border-primary-200 pl-4">
                      <p className="font-medium text-gray-900">{exp.title}</p>
                      <p className="text-gray-600">{exp.company}</p>
                      <p className="text-sm text-gray-400">
                        {exp.start_date} - {exp.end_date || 'Present'}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Languages */}
            {profile.profile_json.languages && profile.profile_json.languages.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-gray-500 mb-2">Languages</h4>
                <p className="text-gray-700">{profile.profile_json.languages.join(', ')}</p>
              </div>
            )}
          </div>

          <p className="mt-6 text-xs text-gray-400">
            Last updated: {new Date(profile.updated_at).toLocaleDateString()}
          </p>
        </section>
      )}
    </div>
  )
}
