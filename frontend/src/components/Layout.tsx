import { Outlet, Link, useLocation } from 'react-router-dom'
import { Disclosure } from '@headlessui/react'

const navigation = [
  { name: '홈', href: '/' },
  { name: '카테고리', href: '/categories' },
  { name: '라이브러리', href: '/library' },
]

export default function Layout() {
  const location = useLocation()

  return (
    <div className="min-h-screen bg-gray-50">
      <Disclosure as="nav" className="bg-white shadow">
        {() => (
          <>
            <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
              <div className="flex h-16 justify-between">
                <div className="flex">
                  <div className="flex flex-shrink-0 items-center">
                    <h1 className="text-xl font-bold text-primary-600">
                      Enhanced Dynamic Content System v6.1
                    </h1>
                  </div>
                  <div className="hidden sm:ml-8 sm:flex sm:space-x-8">
                    {navigation.map((item) => (
                      <Link
                        key={item.name}
                        to={item.href}
                        className={`inline-flex items-center border-b-2 px-1 pt-1 text-sm font-medium ${
                          location.pathname === item.href
                            ? 'border-primary-500 text-gray-900'
                            : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                        }`}
                      >
                        {item.name}
                      </Link>
                    ))}
                  </div>
                </div>
                <div className="flex items-center">
                  <span className="text-sm text-gray-500">
                    AI-Powered Content Generation
                  </span>
                </div>
              </div>
            </div>
          </>
        )}
      </Disclosure>

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <Outlet />
      </main>
    </div>
  )
}