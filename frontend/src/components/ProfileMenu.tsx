import { useEffect, useState } from 'react'
import { fetchProfilePhoto } from '../services/api'
import { UserProfileForm } from './UserProfileForm'

type Props = { email: string; onLogout: () => void }

export function ProfileMenu({ email, onLogout }: Props) {
  const [menuOpen, setMenuOpen] = useState(false)
  const [profileOpen, setProfileOpen] = useState(false)
  const [photoUrl, setPhotoUrl] = useState<string | null>(null)

  useEffect(() => {
    let currentUrl: string | null = null
    void fetchProfilePhoto().then((photo) => {
      if (!photo) return
      currentUrl = URL.createObjectURL(photo)
      setPhotoUrl(currentUrl)
    }).catch(() => undefined)
    return () => {
      if (currentUrl) URL.revokeObjectURL(currentUrl)
    }
  }, [])

  return <>
    <div className="user-menu">
      <button type="button" className="profile-avatar-button" aria-label="Abrir menu do perfil" aria-expanded={menuOpen} onClick={() => setMenuOpen((open) => !open)}>
        {photoUrl ? <img className="profile-avatar" src={photoUrl} alt="Foto de perfil" /> : <span className="profile-avatar profile-avatar-placeholder" aria-hidden="true">♙</span>}
      </button>
      {menuOpen && <div className="dropdown-menu">
        <span>{email}</span>
        <button type="button" onClick={() => { setProfileOpen(true); setMenuOpen(false) }}>Minha conta</button>
        <button type="button" onClick={onLogout}>Sair</button>
      </div>}
    </div>
    {profileOpen && <UserProfileForm email={email} onClose={() => setProfileOpen(false)} onSaved={() => { setProfileOpen(false); window.location.reload() }} />}
  </>
}
