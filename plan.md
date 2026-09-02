# Landing Page Portofolio Developer Modern â Rencana Produk (PRD)

## 1. Ringkasan Produk

Landing page portofolio satu halaman (single-page) untuk developer yang ingin menampilkan identitas profesional, keahlian, proyek unggulan, pengalaman, dan cara menghubungi secara modern, cepat, dan responsif.

### Tujuan
- Meningkatkan personal branding developer.
- Menjadi "wajah digital" yang pertama dilihat recruiter/klien.
- Mengkonversi pengunjung menjadi kontak (hire / kolaborasi).

### Target Pengguna
- Recruiter & HR yang mencari kandidat.
- Klien / startup yang mencari developer freelance.
- Sesama developer (kolaborasi, open source).

---

## 2. Stack Teknologi (Rekomendasi)

| Layer | Teknologi |
|-------|-----------|
| Framework | Next.js (App Router) + TypeScript |
| Styling | Tailwind CSS |
| Animasi | Framer Motion |
| Icons | Lucide React |
| Deploy | Vercel |
| Form kontak | Email (Resend) atau Formspree |
| SEO | Next.js Metadata API + Open Graph |

> **Alternatif ringan:** Vite + React + Tailwind (static, tanpa server).
> **Alternatif tanpa build:** HTML + CSS + Vanilla JS (jika ingin super ringan).

---

## 3. Struktur Halaman (Sections)

1. **Navbar** â Logo/nama, link navigasi, tombol CTA "Hire Me".
2. **Hero** â Nama, role (tagline), foto/avatar, CTA utama, sosial media.
3. **About** â Deskripsi singkat, highlight karir, stats (tahun pengalaman, proyek, klien).
4. **Skills / Tech Stack** â Grid ikon teknologi + kategori (Frontend, Backend, Tools).
5. **Projects** â Kartu proyek (thumbnail, judul, deskripsi, tech, link live & repo).
6. **Experience / Timeline** â Riwayat kerja & pendidikan.
7. **Testimonials** (opsional) â Kutipan klien/kolega.
8. **Contact** â Form kontak + email + sosial media.
9. **Footer** â Copyright, links, back to top.

---

## 4. Database / Data Model

Portofolio bersifat statis, data disimpan sebagai file konfigurasi JSON/TS:

```ts
// data/profile.ts
{
  name: string;
  role: string;
  tagline: string;
  avatar: string;
  email: string;
  location: string;
  resumeUrl: string;
  socials: [{ label, url, icon }];
}

// data/projects.ts
{
  title: string;
  slug: string;
  description: string;
  image: string;
  techStack: string[];
  liveUrl: string;
  repoUrl: string;
  featured: boolean;
}

// data/experience.ts
{
  role: string;
  company: string;
  period: string;
  description: string;
  type: 'work' | 'education';
}

// data/skills.ts
{
  category: string;
  items: [{ name: string; level: number; icon: string }];
}
```

---

## 5. Desain & UI/UX

### Tema Visual
- **Mode:** Dark mode default + toggle light mode.
- **Warna:** Background gelap (`#0a0a0a`), aksen gradient (mis. indigo â cyan).
- **Tipografi:** Inter / Space Grotesk (font modern).
- **Gaya:** Glassmorphism halus, rounded corners, subtle glow.

### ASCII Mockup

```
ââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
â  â YourName        About  Skills  Projects  [Hire] â  â Navbar (sticky)
ââââââââââââââââââââââââââââââââââââââââââââââââââââââââ¤
â                                                      â
â          ð¤ [Avatar / Ilustrasi]                     â
â      Hi, I'm Your Name                               â
â      Full-Stack Developer                            â
â   Building scalable web apps with â¥                 â
â                                                      â
â      [View My Work]   [Download CV]                  â
â      ï GitHub   ï¡ LinkedIn   ï Twitter               â
â                                                      â
ââââââââââââââââââââââââââââââââââââââââââââââââââââââââ¤
â  ABOUT                    âââââââââ¬ââââââââ¬ââââââââ â
â  Short bio text...        â 5+    â 20+   â 10+   â â
â                           â Years â Proj. âClient â â
â                           âââââââââ´ââââââââ´ââââââââ â
ââââââââââââââââââââââââââââââââââââââââââââââââââââââââ¤
â  SKILLS                                            â
â  [Frontend]  [Backend]   [DevOps]  [Tools]         â
â  React  Next  TS   Node  Postgres  Docker ...      â
ââââââââââââââââââââââââââââââââââââââââââââââââââââââââ¤
â  PROJECTS                                          â
â  âââââââââââ  âââââââââââ  âââââââââââ            â
â  â  img    â  â  img    â  â  img    â            â
â  â Title   â  â Title   â  â Title   â            â
â  â desc... â  â desc... â  â desc... â            â
â  â [Live]  â  â [Live]  â  â [Live]  â            â
â  âââââââââââ  âââââââââââ  âââââââââââ            â
ââââââââââââââââââââââââââââââââââââââââââââââââââââââââ¤
â  EXPERIENCE (Timeline)                             â
â  â 2023 - now  Senior Dev @ Company A              â
â  â 2021 - 2023 Dev @ Company B                     â
â  â 2017 - 2021 CS Degree                           â
ââââââââââââââââââââââââââââââââââââââââââââââââââââââââ¤
â  CONTACT                                          â
â  [ Nama     ]  [ Email     ]                      â
â  [ Message                         ]               â
â  [          Send Message           ]               â
â  â email@x.com   ï phone   ï¯ location             â
ââââââââââââââââââââââââââââââââââââââââââââââââââââââââ¤
â  Â© 2025 YourName. Built with Next.js   [Back to â]â
ââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
```

---

## 6. Fitur Utama (MVP)

1. **Hero dinamis** dengan animasi masuk (fade/slide).
2. **Grid proyek** responsif (1/2/3 kolom) + filter kategori.
3. **Skills** dengan progress bar / icon grid.
4. **Dark/Light mode toggle** (tersimpan di localStorage).
5. **Form kontak** fungsional (kirim ke email).
6. **Responsive** penuh (mobile-first).
7. **SEO & OG tags** + favicon.

### Fitur Lanjutan (Nice-to-have)
- Blog section terintegrasi.
- Sertifikat / awards.
- Download CV (PDF).
- Animasi scroll reveal (Framer Motion `whileInView`).
- Pengunjung counter / analitik sederhana.

---

## 7. Struktur Proyek (Next.js)

```
portfolio/
âââ app/
â   âââ layout.tsx
â   âââ page.tsx
â   âââ globals.css
âââ components/
â   âââ Navbar.tsx
â   âââ Hero.tsx
â   âââ About.tsx
â   âââ Skills.tsx
â   âââ Projects.tsx
â   âââ Experience.tsx
â   âââ Contact.tsx
â   âââ Footer.tsx
âââ data/
â   âââ profile.ts
â   âââ projects.ts
â   âââ experience.ts
â   âââ skills.ts
âââ public/
â   âââ images/
âââ tailwind.config.ts
```

---

## 8. Roadmap Implementasi

| Fase | Deliverable | Estimasi |
|------|-------------|----------|
| 1. Setup | Init project, Tailwind, font, struktur folder | 1 jam |
| 2. Data | Isi file data (profile, projects, skills) | 1 jam |
| 3. Layout | Navbar + Hero + Footer | 2-3 jam |
| 4. Sections | About, Skills, Projects, Experience, Contact | 3-4 jam |
| 5. Polish | Animasi, dark mode, responsive, SEO | 2 jam |
| 6. Deploy | Push ke GitHub + deploy Vercel | 30 menit |

**Total estimasi: Â± 10 jam** untuk MVP lengkap.

---

## 9. Kriteria Sukses (KPI)

- PageSpeed / Lighthouse: Performance â¥ 90.
- Fully responsive (mobile, tablet, desktop).
- Konversi kontak: minimal 1 CTA jelas di setiap viewport.
- Load time < 3 detik.
- Skor SEO & Accessibility â¥ 90.

---

## 10. Langkah Selanjutnya

1. Konfirmasi stack (Next.js vs Vite vs vanilla HTML).
2. Siapkan konten personal (nama, bio, foto, proyek).
3. Implementasi kode per fase roadmap.
4. Deploy dan uji di berbagai perangkat.

---

*Dokumen ini siap dikembangkan menjadi kode. Beri tahu saya stack yang Anda inginkan untuk mulai implementasi.*
