import sys
import os

content = open('frontend/src/App.tsx').read()

# 1. Update imports
content = content.replace(
    "Download, History, LayoutDashboard } from 'lucide-react';",
    "Download, History, LayoutDashboard, Search } from 'lucide-react';"
)

# 2. Add state
if "const [editingPrompt, setEditingPrompt] = useState<Prompt | null>(null);" in content:
    content = content.replace(
        "const [editingPrompt, setEditingPrompt] = useState<Prompt | null>(null);",
        "const [editingPrompt, setEditingPrompt] = useState<Prompt | null>(null);\n  const [searchQuery, setSearchQuery] = useState('');"
    )

# 3. Update fetchPrompts
old_fetch = """  const fetchPrompts = async (pageNum = 1, append = false) => {
    if (pageNum === 1 && !append) setLoading(true);
    else setIsFetchingMore(true);

    try {
      const response = await fetch(`/api/prompts?page=${pageNum}&per_page=12`);
      const data = await response.json();"""

new_fetch = """  const fetchPrompts = async (pageNum = 1, append = false) => {
    if (pageNum === 1 && !append) setLoading(true);
    else setIsFetchingMore(true);

    try {
      const endpoint = searchQuery
        ? `/api/prompts/search?q=${encodeURIComponent(searchQuery)}&page=${pageNum}&per_page=12`
        : `/api/prompts?page=${pageNum}&per_page=12`;
      const response = await fetch(endpoint);
      const data = await response.json();"""

content = content.replace(old_fetch, new_fetch)

# 4. Add debounced search effect
old_effect = """  useEffect(() => {
    if (view === 'library') {
      setPage(1);
      fetchPrompts(1, false);
    }
  }, [view]);"""

new_effect = """  useEffect(() => {
    const timer = setTimeout(() => {
      if (view === 'library') {
        setPage(1);
        fetchPrompts(1, false);
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery, view]);"""

content = content.replace(old_effect, new_effect)

# 5. Add search bar UI
search_bar_ui = """              <div className="relative w-full md:w-96 group">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 group-focus-within:text-palette-primary transition-colors" size={18} />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search computational directives..."
                  className="w-full pl-12 pr-4 py-3 bg-white border border-gray-100 rounded-2xl shadow-sm focus:ring-4 focus:ring-palette-primary/5 focus:border-palette-primary outline-none transition-all font-medium text-sm"
                />
              </div>"""

# Insert before Archive text
archive_header = """              <div>
                <h2 className="text-3xl font-black text-palette-dark tracking-tighter uppercase">ARCHIVE</h2>
                <p className="text-gray-400 font-medium mt-1">History of computational directives.</p>
              </div>"""

if archive_header in content:
    content = content.replace(archive_header, search_bar_ui + archive_header)

with open('frontend/src/App.tsx', 'w') as f:
    f.write(content)
