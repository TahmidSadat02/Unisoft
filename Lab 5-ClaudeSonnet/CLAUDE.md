# Project Instructions & Guide (CLAUDE.md)

## Workspace Overview
This repository contains the **REST-API_Adv.-Web-tech** full-stack coffee shop management system.

### Tech Stack
- **Backend**: NestJS (TypeScript), TypeORM, PostgreSQL, Swagger (`REST-API_Adv.-Web-tech/backend`)
- **Frontend**: Next.js 16 (React 19, Tailwind CSS, Axios) (`REST-API_Adv.-Web-tech/frontend`)

---

## Quick Reference Commands

### Backend (`REST-API_Adv.-Web-tech/backend`)
- **Development Server**: `npm run start:dev` (runs on `http://localhost:5001`)
- **Build**: `npm run build`
- **Testing**: `npm run test` or `npm run test:e2e`
- **Swagger Documentation**: `http://localhost:5001/api`

### Frontend (`REST-API_Adv.-Web-tech/frontend`)
- **Development Server**: `npm run dev` (runs on `http://localhost:3000`)
- **Build**: `npm run build`
- **Lint**: `npm run lint`

---

## Coding Guidelines
1. **TypeScript & NestJS**: Maintain strong typing, modular controllers, services, and TypeORM entities.
2. **Environment Variables**: Configure variables in `.env` (copied from `.env.example`).
3. **Error Handling**: Use standard HTTP exception filters in NestJS and proper API response handling in Next.js.
