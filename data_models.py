"""
Pydantic models for structured document data extraction
"""

from typing import List, Optional, Union
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, Field, validator, EmailStr
import re


class ContactInfo(BaseModel):
    """Contact information model"""
    name: Optional[str] = Field(None, description="Full name or company name")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    address: Optional[str] = Field(None, description="Full address")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State or province")
    postal_code: Optional[str] = Field(None, description="ZIP or postal code")
    country: Optional[str] = Field(None, description="Country")

    @validator('phone')
    def clean_phone(cls, v):
        if v:
            # Remove common phone formatting
            return re.sub(r'[^\d+\-\(\)\s]', '', v).strip()
        return v

    @validator('email')
    def validate_email(cls, v):
        if v and '@' in v:
            return v.lower().strip()
        return v


class LineItem(BaseModel):
    """Individual line item in an invoice/receipt"""
    item_name: Optional[str] = Field(None, description="Name or description of the item")
    quantity: Optional[Union[int, float]] = Field(None, description="Quantity of items")
    unit_price: Optional[Decimal] = Field(None, description="Price per unit")
    total_price: Optional[Decimal] = Field(None, description="Total price for this line item")
    item_code: Optional[str] = Field(None, description="Product/item code or SKU")
    category: Optional[str] = Field(None, description="Item category")
    
    @validator('unit_price', 'total_price', pre=True)
    def parse_price(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            # Remove currency symbols and clean up
            cleaned = re.sub(r'[^\d.,\-]', '', v)
            if cleaned:
                try:
                    return Decimal(cleaned.replace(',', ''))
                except:
                    return None
        return v


class TaxInfo(BaseModel):
    """Tax information"""
    tax_rate: Optional[float] = Field(None, description="Tax rate as percentage")
    tax_amount: Optional[Decimal] = Field(None, description="Tax amount in currency")
    tax_type: Optional[str] = Field(None, description="Type of tax (VAT, GST, Sales Tax, etc.)")
    
    @validator('tax_amount', pre=True)
    def parse_tax_amount(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            cleaned = re.sub(r'[^\d.,\-]', '', v)
            if cleaned:
                try:
                    return Decimal(cleaned.replace(',', ''))
                except:
                    return None
        return v


class PaymentInfo(BaseModel):
    """Payment information"""
    payment_method: Optional[str] = Field(None, description="Payment method (cash, card, check, etc.)")
    payment_terms: Optional[str] = Field(None, description="Payment terms")
    due_date: Optional[date] = Field(None, description="Payment due date")
    paid_amount: Optional[Decimal] = Field(None, description="Amount already paid")
    balance_due: Optional[Decimal] = Field(None, description="Remaining balance")
    
    @validator('paid_amount', 'balance_due', pre=True)
    def parse_amount(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            cleaned = re.sub(r'[^\d.,\-]', '', v)
            if cleaned:
                try:
                    return Decimal(cleaned.replace(',', ''))
                except:
                    return None
        return v


class DocumentInfo(BaseModel):
    """Document metadata"""
    document_type: Optional[str] = Field(None, description="Type of document (invoice, receipt, bill, etc.)")
    document_number: Optional[str] = Field(None, description="Invoice/receipt number")
    document_date: Optional[date] = Field(None, description="Document date")
    reference_number: Optional[str] = Field(None, description="Reference or PO number")
    
    @validator('document_date', pre=True)
    def parse_date(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            # Try to parse common date formats
            date_patterns = [
                r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',
                r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',
                r'(\d{1,2})[/-](\d{1,2})[/-](\d{2})'
            ]
            for pattern in date_patterns:
                match = re.search(pattern, v)
                if match:
                    try:
                        groups = match.groups()
                        if len(groups[2]) == 2:  # 2-digit year
                            year = int(groups[2])
                            year = 2000 + year if year < 50 else 1900 + year
                        else:
                            year = int(groups[2])
                        
                        # Assume first pattern is MM/DD/YYYY
                        if pattern == date_patterns[0]:
                            return date(year, int(groups[0]), int(groups[1]))
                        else:  # YYYY/MM/DD
                            return date(year, int(groups[1]), int(groups[2]))
                    except:
                        continue
        return v


class StructuredDocument(BaseModel):
    """Complete structured document model"""
    # Document metadata
    document_info: DocumentInfo = Field(default_factory=DocumentInfo)
    
    # Vendor/Company information
    vendor: ContactInfo = Field(default_factory=ContactInfo, description="Vendor/company information")
    
    # Customer/Bill-to information
    customer: ContactInfo = Field(default_factory=ContactInfo, description="Customer/bill-to information")
    
    # Line items
    line_items: List[LineItem] = Field(default_factory=list, description="List of items/services")
    
    # Financial information
    subtotal: Optional[Decimal] = Field(None, description="Subtotal before tax")
    tax_info: TaxInfo = Field(default_factory=TaxInfo)
    total_amount: Optional[Decimal] = Field(None, description="Total amount including tax")
    
    # Payment information
    payment_info: PaymentInfo = Field(default_factory=PaymentInfo)
    
    # Additional fields
    notes: Optional[str] = Field(None, description="Additional notes or comments")
    currency: Optional[str] = Field("USD", description="Currency code")
    
    # Processing metadata
    source_filename: Optional[str] = Field(None, description="Source image filename")
    processed_at: Optional[datetime] = Field(default_factory=datetime.now)
    confidence_score: Optional[float] = Field(None, description="Extraction confidence (0-1)")
    
    @validator('subtotal', 'total_amount', pre=True)
    def parse_amounts(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            cleaned = re.sub(r'[^\d.,\-]', '', v)
            if cleaned:
                try:
                    return Decimal(cleaned.replace(',', ''))
                except:
                    return None
        return v

    def to_flat_dict(self) -> dict:
        """Convert to flat dictionary for CSV export"""
        flat_dict = {
            # Document info
            'document_type': self.document_info.document_type,
            'document_number': self.document_info.document_number,
            'document_date': self.document_info.document_date,
            'reference_number': self.document_info.reference_number,
            
            # Vendor info
            'vendor_name': self.vendor.name,
            'vendor_email': self.vendor.email,
            'vendor_phone': self.vendor.phone,
            'vendor_address': self.vendor.address,
            'vendor_city': self.vendor.city,
            'vendor_state': self.vendor.state,
            'vendor_postal_code': self.vendor.postal_code,
            'vendor_country': self.vendor.country,
            
            # Customer info
            'customer_name': self.customer.name,
            'customer_email': self.customer.email,
            'customer_phone': self.customer.phone,
            'customer_address': self.customer.address,
            'customer_city': self.customer.city,
            'customer_state': self.customer.state,
            'customer_postal_code': self.customer.postal_code,
            'customer_country': self.customer.country,
            
            # Financial info
            'subtotal': float(self.subtotal) if self.subtotal else None,
            'tax_rate': self.tax_info.tax_rate,
            'tax_amount': float(self.tax_info.tax_amount) if self.tax_info.tax_amount else None,
            'tax_type': self.tax_info.tax_type,
            'total_amount': float(self.total_amount) if self.total_amount else None,
            'currency': self.currency,
            
            # Payment info
            'payment_method': self.payment_info.payment_method,
            'payment_terms': self.payment_info.payment_terms,
            'due_date': self.payment_info.due_date,
            'paid_amount': float(self.payment_info.paid_amount) if self.payment_info.paid_amount else None,
            'balance_due': float(self.payment_info.balance_due) if self.payment_info.balance_due else None,
            
            # Additional
            'notes': self.notes,
            'source_filename': self.source_filename,
            'processed_at': self.processed_at,
            'confidence_score': self.confidence_score,
        }
        
        # Add line items (for first item only in main row, or create separate rows)
        if self.line_items:
            first_item = self.line_items[0]
            flat_dict.update({
                'item_name': first_item.item_name,
                'quantity': first_item.quantity,
                'unit_price': float(first_item.unit_price) if first_item.unit_price else None,
                'item_total_price': float(first_item.total_price) if first_item.total_price else None,
                'item_code': first_item.item_code,
                'item_category': first_item.category,
                'total_line_items': len(self.line_items)
            })
        else:
            flat_dict.update({
                'item_name': None,
                'quantity': None,
                'unit_price': None,
                'item_total_price': None,
                'item_code': None,
                'item_category': None,
                'total_line_items': 0
            })
        
        return flat_dict

    def to_line_items_list(self) -> List[dict]:
        """Convert to list of dictionaries, one per line item"""
        if not self.line_items:
            return [self.to_flat_dict()]
        
        base_dict = self.to_flat_dict()
        result = []
        
        for i, item in enumerate(self.line_items):
            item_dict = base_dict.copy()
            item_dict.update({
                'item_name': item.item_name,
                'quantity': item.quantity,
                'unit_price': float(item.unit_price) if item.unit_price else None,
                'item_total_price': float(item.total_price) if item.total_price else None,
                'item_code': item.item_code,
                'item_category': item.category,
                'line_item_number': i + 1
            })
            result.append(item_dict)
        
        return result
