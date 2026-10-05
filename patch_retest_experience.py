# -*- coding: utf-8 -*-
import re

# 1. Update web/style.css with required classes
css_addon = """
/* Selected during exam without spoiling answer */
.option-btn.selected-exam, .judge-btn.selected-exam {
  background: var(--accent-light) !important;
  border-color: var(--accent-color) !important;
  color: var(--accent-color) !important;
  font-weight: 700;
}

/* Wrong question conquered banner */
.conquer-banner {
  background: var(--success-light);
  border: 1px solid var(--success-color);
  border-radius: var(--radius-sm);
  padding: 10px 14px;
  margin-top: 10px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  color: var(--success-color);
  font-size: 0.85rem;
}

.action-btn.mini {
  padding: 6px 12px;
  font-size: 0.78rem;
  min-height: 32px;
  flex: initial;
}

/* Card re-test button */
.re-test-btn {
  background: none;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 4px 10px;
  font-size: 0.76rem;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.15s;
}
.re-test-btn:hover {
  background: var(--accent-light);
  border-color: var(--accent-color);
  color: var(--accent-color);
}
"""

with open("/Volumes/Ext/dev/python/pdf_compressor/web/style.css", "a", encoding="utf-8") as f:
    f.write(css_addon)

print("Updated web/style.css with re-test classes!")
